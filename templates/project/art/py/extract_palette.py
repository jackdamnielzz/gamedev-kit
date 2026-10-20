"""Extract a project palette from approved reference images with k-means (numpy only).

Writes art/palette.json (linear RGB 0-1 for Blender, plus sRGB hex for 2D tools) and a swatch PNG.
Name the colours afterwards (replace "c01" etc. with hull, trim, skin ...).

Usage: python art/py/extract_palette.py art/refs/units/*.png --k 10 --out art/palette.json
"""
import argparse
import glob
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def load_pixels(paths, tol=40, max_px=200_000):
    chunks = []
    for path in paths:
        img = Image.open(path).convert("RGBA")
        img.thumbnail((512, 512))
        a = np.asarray(img).reshape(-1, 4).astype(float)
        a = a[a[:, 3] > 128][:, :3]                      # skip transparent pixels
        border_bg = np.median(np.asarray(img.convert("RGB"))[0], axis=0)
        a = a[np.abs(a - border_bg).sum(axis=1) > tol]   # skip the flat background
        chunks.append(a)
    px = np.concatenate(chunks) if chunks else np.zeros((0, 3))
    if len(px) > max_px:
        px = px[np.random.default_rng(0).choice(len(px), max_px, replace=False)]
    return px


def kmeans(px, k, iters=30):
    rng = np.random.default_rng(0)
    centers = px[rng.choice(len(px), k, replace=False)]
    for _ in range(iters):
        labels = np.argmin(((px[:, None] - centers[None]) ** 2).sum(axis=2), axis=1)
        new = np.array([px[labels == i].mean(axis=0) if np.any(labels == i) else centers[i] for i in range(k)])
        if np.allclose(new, centers):
            break
        centers = new
    counts = np.bincount(labels, minlength=k)
    order = np.argsort(-counts)
    return centers[order], counts[order]


def srgb_to_linear(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("images", nargs="+")
    p.add_argument("--k", type=int, default=10)
    p.add_argument("--out", default="art/palette.json")
    a = p.parse_args()

    paths = [m for pattern in a.images for m in (sorted(glob.glob(pattern)) or [pattern])]
    px = load_pixels(paths)
    if len(px) < a.k:
        raise SystemExit("not enough foreground pixels")
    centers, counts = kmeans(px, a.k)

    palette = {"_source": paths, "_note": "linear RGB 0-1; rename keys to meaningful names"}
    swatch = Image.new("RGB", (64 * a.k, 80), "white")
    draw = ImageDraw.Draw(swatch)
    for i, (c, n) in enumerate(zip(centers, counts)):
        rgb = tuple(int(round(v)) for v in c)
        hexv = "#%02x%02x%02x" % rgb
        palette[f"c{i + 1:02d}"] = [round(float(v), 4) for v in srgb_to_linear(np.array(c))]
        palette.setdefault("_hex", {})[f"c{i + 1:02d}"] = hexv
        draw.rectangle([i * 64, 0, i * 64 + 63, 63], fill=rgb)
        draw.text((i * 64 + 4, 66), f"c{i + 1:02d}", fill="black")

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(palette, indent=2))
    swatch_path = Path("build/previews") / "palette_swatches.png"
    swatch_path.parent.mkdir(parents=True, exist_ok=True)
    swatch.save(swatch_path)
    print(json.dumps({"colours": a.k, "palette": str(out), "swatches": str(swatch_path)}))


main()
