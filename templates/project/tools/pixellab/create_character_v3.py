"""PIXEL ART ONLY (PixelLab). Turn an approved south-facing pixel-art sprite into a PixelLab
character (v3, 4 or 8 directions).

  # dry run: checks the sprite, shows the cost and the request, sends nothing
  python tools/pixellab/create_character_v3.py hero --sprite art/refs/characters/hero_south.png \
      --description "young knight in dented steel armour, red cloak"
  # generate (refuses above --max-generations, and refuses to re-create an existing character)
  python tools/pixellab/create_character_v3.py hero --sprite ... --description "..." --run
  # resume / download only (free): after an interruption, or for an existing PixelLab character
  python tools/pixellab/create_character_v3.py hero --resume
  python tools/pixellab/create_character_v3.py hero --character-id <pixellab character id>
  # redo all post-processing from the downloaded files (offline, free)
  python tools/pixellab/create_character_v3.py hero --rebuild [--palette art/palette.json | --palette auto]

Cost: ceil(w*h*directions/65536) generations (64x64 with 8 directions = 1); the real cost is
measured from the balance before and after. The character id is saved to
build/gen/characters/<name>/state.json the moment PixelLab returns it, so an interrupted run never
loses a paid character.

After the download (or with --rebuild, offline and free) every run post-processes:
  1. palette snap: all directions onto ONE palette (art/palette.json, or a shared auto palette when the
     project has none yet), binary alpha -> final/<direction>.png; the raw PixelLab files stay untouched
  2. lint per direction: palette only, no semi-transparent pixels, no orphan pixels, not upscaled
  3. sheet.png + sheet.json (one row, equal cells, never rescaled, bottom-centre pivot), a labelled 4x
     preview and a turnaround GIF in build/previews/
  4. review page build/previews/<name>_review.html: raw vs final, 1x and 4x, light and dark, the GIF,
     warnings and lint results, for the human to approve
  5. Phaser atlas export/<name>.png + export/<name>.json (TexturePacker JSON Hash, frames
     '<name>/<direction>', pivot bottom-centre): this.load.atlas('<name>', png, json)
  6. report.json, a line in build/gen/log.jsonl, and manifest entries when assets/manifest.json exists
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import (DIRECTIONS, GEN_DIR, PREVIEW_DIR, ROOT, Client, PixelLabError, add_to_manifest,  # noqa: E402
                    append_log, image_payload, labelled_sheet, lint, load_palette, log, phaser_atlas,
                    review_page, sha256, shared_palette, snap, spritesheet, sprite_stats, turn_gif)

LICENCE = "PixelLab subscription: commercial use allowed, no training of models on the output"


def rel(p: Path) -> str:
    """Project-relative POSIX path (falls back to the absolute path outside the project)."""
    p = Path(p).resolve()
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def project_path(value: str | None) -> Path | None:
    if not value:
        return None
    p = Path(value)
    return p if p.is_absolute() else (ROOT / p)


def check_sprite(path: Path) -> tuple[Image.Image, list[str]]:
    if not path.exists():
        raise SystemExit(f"sprite not found: {path}")
    img = Image.open(path)
    problems, warnings = [], []
    if img.width > 256 or img.height > 256:
        problems.append(f"sprite is {img.width}x{img.height}; v3 accepts at most 256x256 (crop, never rescale)")
    if img.mode != "RGBA" or img.getchannel("A").getextrema() == (255, 255):
        warnings.append("sprite has no transparency; PixelLab will key the background itself")
    img = img.convert("RGBA")
    stats = sprite_stats(img)
    if stats["height"] == 0:
        problems.append("sprite is fully transparent")
    if stats["semi_transparent"]:
        warnings.append(f"{stats['semi_transparent']} semi-transparent pixels; real pixel art uses binary alpha")
    if stats["bbox"] and (stats["bbox"][1] == 0 or stats["bbox"][3] == img.height):
        warnings.append("the figure touches the top or bottom edge; animations may need more room")
    warnings.append("v3 treats the sprite as SOUTH (facing the viewer); a turned sprite shifts all labels by 45 degrees")
    if problems:
        raise SystemExit("sprite rejected:\n  - " + "\n  - ".join(problems))
    return img, warnings


def report(frames: list[tuple[str, Image.Image]], source_height: int) -> dict:
    per = {name: sprite_stats(f) for name, f in frames}
    sizes = {f.size for _, f in frames}
    heights = [s["height"] for s in per.values() if s["height"]]
    warnings = []
    if len(sizes) > 1:
        warnings.append(f"frames have different canvas sizes: {sorted(sizes)}")
    if heights and max(heights) - min(heights) > max(3, source_height * 0.08):
        warnings.append(f"figure height varies from {min(heights)} to {max(heights)} px between directions")
    for name, s in per.items():
        if s["semi_transparent"]:
            warnings.append(f"{name}: {s['semi_transparent']} semi-transparent pixels")
    return {"directions": per, "canvas_sizes": sorted(sizes), "height_range": [min(heights), max(heights)] if heights else None,
            "warnings": warnings}


def download(client: Client, name: str, char_id: str, out_dir: Path) -> None:
    """Fetch the finished rotations from PixelLab into out_dir/<direction>.png (the raw files)."""
    info = client.wait_for(f"/characters/{char_id}", f"character {name}")
    (out_dir / "character.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    urls = info.get("rotation_urls") or {}
    saved = 0
    for direction in DIRECTIONS:
        url = urls.get(direction)
        if isinstance(url, dict):
            url = url.get("url")
        if url:
            (out_dir / f"{direction}.png").write_bytes(client.download(url))
            saved += 1
    if not saved:
        raise SystemExit("PixelLab returned no rotation images")


def choose_palette(arg: str, colours: int, raw: list[Image.Image]) -> tuple[list, str]:
    """Project palette if it exists and is real (8+ colours), else one shared palette from all frames."""
    path = None if arg == "auto" else project_path(arg)
    if path and path.exists():
        pal = load_palette(path)
        if len(pal) >= 8:
            return pal, rel(path)
        log(f"  {rel(path)} has only {len(pal)} colours (placeholder?); using a shared auto palette instead")
    return shared_palette(raw, colours), f"auto: {colours} colours shared by all directions"


def postprocess(name: str, char_id: str, out_dir: Path, source: Path | None, spent, palette_arg: str,
                colours: int) -> None:
    """Free, offline: palette snap, lint, sheets, review page, Phaser atlas, log and manifest."""
    raw = [(d, Image.open(out_dir / f"{d}.png").convert("RGBA")) for d in DIRECTIONS if (out_dir / f"{d}.png").exists()]
    if not raw:
        raise SystemExit(f"no downloaded rotations in {rel(out_dir)}; run with --resume first")

    # 1. palette snap: every direction onto ONE palette, binary alpha
    palette, palette_source = choose_palette(palette_arg, colours, [f for _, f in raw])
    final_dir = out_dir / "final"
    final_dir.mkdir(exist_ok=True)
    final = [(d, snap(f, palette)) for d, f in raw]
    for d, f in final:
        f.save(final_dir / f"{d}.png")

    # 2. lint every final frame
    lints = {d: lint(f, palette) for d, f in final}

    src_h = sprite_stats(Image.open(source).convert("RGBA"))["height"] if source and source.exists() else 0
    rep = report(final, src_h)
    rep.update({"character_id": char_id, "generations_spent": spent, "source": rel(source) if source else None,
                "palette_source": palette_source, "palette_size": len(palette),
                "palette": ["#%02x%02x%02x" % c for c in palette], "lint": lints,
                "lint_pass": all(l["pass"] for l in lints.values())})
    (out_dir / "report.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")

    # sheets and previews
    spritesheet(final, out_dir / "sheet.png", out_dir / "sheet.json")
    labelled_sheet(final, PREVIEW_DIR / f"{name}_rotations.png")
    gif = PREVIEW_DIR / f"{name}_turn.gif"
    turn_gif(final, gif)

    # 7. review page for the human
    page = PREVIEW_DIR / f"{name}_review.html"
    review_page(name, raw, final, rep, gif, page)

    # 8. Phaser atlas (TexturePacker JSON Hash), frames '<name>/<direction>'
    atlas = phaser_atlas(name, [(f"{name}/{d}", f) for d, f in final], out_dir / "export")

    wrote = add_to_manifest([{
        "path": rel(final_dir / f"{d}.png"), "kind": "generated", "provider": "pixellab",
        "model": "create-character-v3", "pixellab_id": char_id, "built_from": [rel(source)] if source else [],
        "licence": LICENCE, "ai_pixels_shipped": True, "human_edited": False, "approved": False} for d, _ in final])
    append_log({"name": name, "purpose": "character", "provider": "pixellab", "model": "create-character-v3",
                "character_id": char_id, "source": rel(source) if source else None,
                "source_sha256": sha256(source) if source and source.exists() else None,
                "directions": [d for d, _ in final], "generations_spent": spent, "palette": palette_source,
                "lint_pass": rep["lint_pass"], "warnings": rep["warnings"]})
    print(json.dumps({"character_id": char_id, "directions": [d for d, _ in final], "generations_spent": spent,
                      "height_range": rep["height_range"], "palette": f"{palette_source} ({len(palette)})",
                      "lint_pass": rep["lint_pass"], "warnings": rep["warnings"],
                      "review_page": rel(page), "phaser_atlas": [rel(atlas["png"]), rel(atlas["json"])],
                      "manifest_updated": wrote}, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("name", help="asset name, used for the output folder")
    p.add_argument("--sprite", type=Path, help="approved south-facing sprite (PNG, at most 256x256)")
    p.add_argument("--description", help="what the character looks like (noun phrase)")
    p.add_argument("--directions", type=int, choices=(4, 8), default=8)
    p.add_argument("--view", default="low top-down", choices=("low top-down", "high top-down", "side"))
    p.add_argument("--template", default="mannequin", choices=("mannequin", "bear", "cat", "dog", "horse", "lion"))
    p.add_argument("--seed", type=int)
    p.add_argument("--max-generations", type=float, default=5, help="refuse a run estimated above this")
    p.add_argument("--run", action="store_true", help="really generate (costs generations)")
    p.add_argument("--force", action="store_true", help="create a new character even if one exists for this name")
    p.add_argument("--resume", action="store_true", help="download the character saved in state.json (free)")
    p.add_argument("--character-id", help="download an existing PixelLab character (free)")
    p.add_argument("--rebuild", action="store_true",
                   help="redo palette snap, lint, sheets, review page and Phaser export from the downloaded files "
                        "(offline, free)")
    p.add_argument("--palette", default="art/palette.json",
                   help="project palette (art/palette.json); 'auto' or a missing/placeholder file = one shared "
                        "palette built from all directions")
    p.add_argument("--colours", type=int, default=32, help="size of the auto palette")
    a = p.parse_args()

    if a.sprite:
        a.sprite = a.sprite.resolve()
    out_dir = GEN_DIR / "characters" / a.name
    state_path = out_dir / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}

    if a.rebuild:
        source = a.sprite or project_path(state.get("source"))
        postprocess(a.name, state.get("character_id"), out_dir, source, state.get("generations_spent"),
                    a.palette, a.colours)
        return

    if a.resume or a.character_id:
        char_id = a.character_id or state.get("character_id")
        if not char_id:
            raise SystemExit(f"nothing to resume: {state_path} has no character_id")
        out_dir.mkdir(parents=True, exist_ok=True)
        if a.character_id and not state:
            state_path.write_text(json.dumps({"character_id": char_id, "source": rel(a.sprite) if a.sprite else None},
                                             indent=2), encoding="utf-8")
        source = a.sprite or project_path(state.get("source"))
        download(Client(), a.name, char_id, out_dir)
        postprocess(a.name, char_id, out_dir, source, state.get("generations_spent"), a.palette, a.colours)
        return

    if not a.sprite or not a.description:
        raise SystemExit("--sprite and --description are required to create a character")
    img, warnings = check_sprite(a.sprite)
    estimate = math.ceil(img.width * img.height * a.directions / 65536)
    body = {"description": a.description, "name": a.name, "n_directions": a.directions, "view": a.view,
            "template_id": a.template, "no_background": True, "reference_image": image_payload(a.sprite)}
    if a.seed is not None:
        body["seed"] = a.seed
    preview = {k: v for k, v in body.items() if k != "reference_image"}
    print(json.dumps({"sprite": rel(a.sprite), "size": img.size, "request": preview,
                      "estimate_generations": estimate, "warnings": warnings}, indent=2))

    if state.get("character_id") and not a.force:
        raise SystemExit(f"'{a.name}' already has character {state['character_id']} (state.json). "
                         "Use --resume to download it, or --force to pay for a new one.")
    if estimate > a.max_generations:
        raise SystemExit(f"estimate {estimate} > --max-generations {a.max_generations}; ask the human first")
    if not a.run:
        print("dry run: nothing sent. Add --run to generate.")
        return

    client = Client()
    before = client.generations_left()
    if before < estimate:
        raise SystemExit(f"only {before} generations left, need about {estimate}")
    try:
        resp = client.post("/create-character-v3", body)
    except PixelLabError as e:
        raise SystemExit(f"PixelLab refused the request: {e}")
    char_id = resp["character_id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    state = {"character_id": char_id, "job_id": resp.get("background_job_id"), "source": rel(a.sprite),
             "request": preview, "generations_before": before}
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    log(f"character {char_id} submitted (saved to {state_path.relative_to(ROOT)}); waiting ...")

    try:
        client.wait_for(f"/characters/{char_id}", f"character {a.name}")
    except (TimeoutError, KeyboardInterrupt) as e:
        raise SystemExit(f"stopped while waiting ({e.__class__.__name__}); run again with --resume, nothing is lost")
    spent = round(before - client.generations_left(), 2)
    state["generations_spent"] = spent
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    download(client, a.name, char_id, out_dir)
    postprocess(a.name, char_id, out_dir, a.sprite, spent, a.palette, a.colours)


if __name__ == "__main__":
    main()
