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

Cost: ceil(w*h*directions/65536) generations (64x64 with 8 directions = 1); the real cost is
measured from the balance before and after. The character id is saved to
build/gen/characters/<name>/state.json the moment PixelLab returns it, so an interrupted run never
loses a paid character.

Output in build/gen/characters/<name>/: one PNG per direction, sheet.png + sheet.json (one row,
equal cells, never rescaled, bottom-centre pivot), character.json (PixelLab metadata), report.json
(size, height, colours per direction, warnings), and build/previews/<name>_rotations.png (labelled,
4x). If assets/manifest.json exists, one entry per direction is added (ai_pixels_shipped: true).
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
                    append_log, image_payload, labelled_sheet, log, sha256, spritesheet, sprite_stats)

LICENCE = "PixelLab subscription: commercial use allowed, no training of models on the output"
FOUR = ["south", "east", "north", "west"]


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


def fetch(client: Client, name: str, char_id: str, out_dir: Path, source: Path | None, spent: float | None) -> None:
    info = client.wait_for(f"/characters/{char_id}", f"character {name}")
    (out_dir / "character.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    urls = info.get("rotation_urls") or {}
    order = DIRECTIONS if len(urls) > 4 else FOUR
    frames = []
    for direction in order:
        url = urls.get(direction)
        if isinstance(url, dict):
            url = url.get("url")
        if not url:
            log(f"  warning: no image for {direction}")
            continue
        path = out_dir / f"{direction}.png"
        path.write_bytes(client.download(url))
        frames.append((direction, Image.open(path).convert("RGBA")))
    if not frames:
        raise SystemExit("PixelLab returned no rotation images")

    spritesheet(frames, out_dir / "sheet.png", out_dir / "sheet.json")
    labelled_sheet(frames, PREVIEW_DIR / f"{name}_rotations.png")
    src_h = sprite_stats(Image.open(source).convert("RGBA"))["height"] if source and source.exists() else 0
    rep = report(frames, src_h)
    rep.update({"character_id": char_id, "generations_spent": spent, "source": rel(source) if source else None})
    (out_dir / "report.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")

    wrote = add_to_manifest([{
        "path": rel(out_dir / f"{d}.png"), "kind": "generated", "provider": "pixellab",
        "model": "create-character-v3", "pixellab_id": char_id, "built_from": [rel(source)] if source else [],
        "licence": LICENCE, "ai_pixels_shipped": True, "human_edited": False} for d, _ in frames])
    append_log({"name": name, "purpose": "character", "provider": "pixellab", "model": "create-character-v3",
                "character_id": char_id, "source": rel(source) if source else None,
                "source_sha256": sha256(source) if source and source.exists() else None,
                "directions": [d for d, _ in frames], "generations_spent": spent, "warnings": rep["warnings"]})
    print(json.dumps({"character_id": char_id, "saved": [d for d, _ in frames], "generations_spent": spent,
                      "height_range": rep["height_range"], "warnings": rep["warnings"],
                      "preview": rel(PREVIEW_DIR / f"{name}_rotations.png"), "manifest_updated": wrote}, indent=2))


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
    a = p.parse_args()

    if a.sprite:
        a.sprite = a.sprite.resolve()
    out_dir = GEN_DIR / "characters" / a.name
    state_path = out_dir / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}

    if a.resume or a.character_id:
        char_id = a.character_id or state.get("character_id")
        if not char_id:
            raise SystemExit(f"nothing to resume: {state_path} has no character_id")
        out_dir.mkdir(parents=True, exist_ok=True)
        if a.character_id and not state:
            state_path.write_text(json.dumps({"character_id": char_id, "source": rel(a.sprite) if a.sprite else None},
                                             indent=2), encoding="utf-8")
        source = a.sprite or project_path(state.get("source"))
        fetch(Client(), a.name, char_id, out_dir, source, state.get("generations_spent"))
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
    fetch(client, a.name, char_id, out_dir, a.sprite, spent)


if __name__ == "__main__":
    main()
