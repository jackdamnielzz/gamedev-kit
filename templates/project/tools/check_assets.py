"""`npm run assets:check`: every shipped file has a manifest entry with a licence, and nothing in the
manifest is stale. Standard library only, so CI needs no extra installs.

  python tools/check_assets.py                 # check (exit 1 on problems)
  python tools/check_assets.py --hash <file>   # print the hash to store as build_script_hash

Rules (assets/manifest.json, see its "_schema"):
  1. Every file under public/assets/ (and under assets/ for a Godot project) matches an entry
     whose kind is "shipped". An entry's path may be a glob ("public/assets/units/tank_*.png").
  2. Every entry has a licence; shipped entries say ai_pixels_shipped true or false.
  3. Every path in an entry (and in built_from) exists.
  4. If an entry has recipe + build_script_hash, the recipe file still has that hash; otherwise
     the recipe changed and its outputs were not rebuilt.
"""
import argparse
import fnmatch
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets" / "manifest.json"
SHIPPED_DIRS = ["public/assets"]
IGNORE = {".gitkeep", ".DS_Store", "Thumbs.db"}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def shipped_files() -> list[str]:
    dirs = list(SHIPPED_DIRS)
    if (ROOT / "project.godot").exists():
        dirs.append("assets")
    files = []
    for d in dirs:
        base = ROOT / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*")):
            rel = p.relative_to(ROOT).as_posix()
            if p.is_file() and p.name not in IGNORE and not p.name.endswith(".import") and rel != "assets/manifest.json":
                files.append(rel)
    return files


def matches(entry_path: str, rel: str) -> bool:
    return entry_path == rel or fnmatch.fnmatchcase(rel, entry_path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hash", metavar="FILE", help="print the build_script_hash of a recipe or build script")
    a = ap.parse_args()
    if a.hash:
        print(file_hash(Path(a.hash)))
        return 0

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = manifest.get("entries", [])
    problems: list[str] = []

    for i, e in enumerate(entries):
        name = e.get("path", f"entry #{i}")
        kind = e.get("kind")
        if kind not in ("reference", "shipped"):
            problems.append(f"{name}: kind must be 'reference' or 'shipped'")
        if not e.get("licence"):
            problems.append(f"{name}: no licence")
        if kind == "shipped" and not isinstance(e.get("ai_pixels_shipped"), bool):
            problems.append(f"{name}: ai_pixels_shipped must be true or false")
        path = e.get("path", "")
        if not any(ch in path for ch in "*?[") and not (ROOT / path).exists():
            problems.append(f"{name}: file does not exist")
        for ref in e.get("built_from", []) or []:
            if not (ROOT / ref).exists():
                problems.append(f"{name}: built_from {ref} does not exist")
        recipe, stored = e.get("recipe"), e.get("build_script_hash")
        if kind == "shipped" and recipe and stored:
            rp = ROOT / recipe
            if not rp.exists():
                problems.append(f"{name}: recipe {recipe} does not exist")
            elif file_hash(rp) != stored:
                problems.append(f"{name}: {recipe} changed since the asset was built; rebuild it and store the new hash")

    shipped_entries = [e for e in entries if e.get("kind") == "shipped"]
    for rel in shipped_files():
        if not any(matches(e.get("path", ""), rel) for e in shipped_entries):
            problems.append(f"{rel}: shipped file without a manifest entry")

    if problems:
        print(f"assets:check found {len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"assets:check ok ({len(entries)} manifest entries, {len(shipped_files())} shipped files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
