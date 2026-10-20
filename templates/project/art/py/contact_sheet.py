"""Build a labelled contact sheet from several images so the human (and Claude) can compare options.

Usage: python art/py/contact_sheet.py build/gen/explore_units_* --out build/previews/explore_units.png
"""
import argparse
import glob
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

LABEL_H = 28


def main():
    p = argparse.ArgumentParser()
    p.add_argument("images", nargs="+", help="image paths or glob patterns")
    p.add_argument("--out", required=True)
    p.add_argument("--cell", type=int, default=384, help="cell size in px")
    p.add_argument("--cols", type=int, default=0, help="columns (0 = auto)")
    a = p.parse_args()

    paths = []
    for pattern in a.images:
        matches = sorted(glob.glob(pattern)) or [pattern]
        paths += [m for m in matches if Path(m).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
    if not paths:
        raise SystemExit("no images found")

    cols = a.cols or math.ceil(math.sqrt(len(paths)))
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * a.cell, rows * (a.cell + LABEL_H)), (32, 32, 32))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for i, path in enumerate(paths):
        img = Image.open(path).convert("RGBA")
        img.thumbnail((a.cell, a.cell), Image.LANCZOS)
        x, y = (i % cols) * a.cell, (i // cols) * (a.cell + LABEL_H)
        bg = Image.new("RGBA", img.size, (128, 128, 128, 255))
        bg.alpha_composite(img)
        sheet.paste(bg.convert("RGB"), (x + (a.cell - img.width) // 2, y + (a.cell - img.height) // 2))
        label = f"{chr(65 + i) if i < 26 else i}  {Path(path).stem}"
        draw.text((x + 6, y + a.cell + 7), label[:48], fill=(235, 235, 235), font=font)

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(a.out)
    print(f"{len(paths)} images -> {a.out}")


main()
