"""Slice an orthographic turnaround sheet into separate view images.

Expects the views side by side on a flat background (as the turnaround prompt asks). Finds the
columns of non-background pixels, crops each view tight, and pads them to one shared height so
they keep the same scale. Views are named in order (default: front, side, back, top).

Usage:
  python art/py/slice_refs.py art/refs/units/tank_turnaround.png --out art/refs/units/tank
  python art/py/slice_refs.py sheet.png --out dir --names front side top --rows 1
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def foreground(img: Image.Image, tol: int) -> np.ndarray:
    a = np.asarray(img.convert("RGB")).astype(int)
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg = np.median(border, axis=0)
    return np.abs(a - bg).sum(axis=2) > tol


def runs(mask_1d: np.ndarray, min_gap: int, min_len: int):
    """Return (start, end) of runs of True separated by at least min_gap False values."""
    idx = np.flatnonzero(mask_1d)
    if idx.size == 0:
        return []
    out, start, prev = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - prev > min_gap:
            out.append((start, prev + 1))
            start = i
        prev = i
    out.append((start, prev + 1))
    return [(s, e) for s, e in out if e - s >= min_len]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("sheet")
    p.add_argument("--out", required=True, help="output folder for the views")
    p.add_argument("--names", nargs="+", default=["front", "side", "back", "top"])
    p.add_argument("--tol", type=int, default=40, help="background tolerance (sum of RGB diff)")
    p.add_argument("--gap", type=int, default=0, help="min gap between views in px (0 = 1%% of width)")
    a = p.parse_args()

    img = Image.open(a.sheet).convert("RGBA")
    fg = foreground(img, a.tol)
    h, w = fg.shape
    gap = a.gap or max(4, w // 100)

    # The swatch row (if any) sits below the views: use the tallest band of rows first.
    row_bands = runs(fg.any(axis=1), min_gap=gap, min_len=h // 20)
    if not row_bands:
        raise SystemExit("no foreground found; check --tol")
    top, bottom = max(row_bands, key=lambda r: r[1] - r[0])
    band = fg[top:bottom]

    cols = runs(band.any(axis=0), min_gap=gap, min_len=w // 40)
    if len(cols) != len(a.names):
        print(f"warning: found {len(cols)} views, expected {len(a.names)}; naming the first ones in order")

    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {"sheet": a.sheet, "views": {}}
    max_h = 0
    crops = []
    for (x0, x1), name in zip(cols, a.names):
        sub = band[:, x0:x1]
        ys = np.flatnonzero(sub.any(axis=1))
        y0, y1 = top + ys[0], top + ys[-1] + 1
        crop = img.crop((x0, y0, x1, y1))
        # make the background transparent so Blender reference planes overlay cleanly
        alpha = Image.fromarray((fg[y0:y1, x0:x1] * 255).astype(np.uint8))
        crop.putalpha(alpha)
        crops.append((name, crop, int(bottom - y1)))
        max_h = max(max_h, y1 - y0)
        meta["views"][name] = {"box": [int(x0), int(y0), int(x1), int(y1)]}

    for name, crop, _ in crops:
        canvas = Image.new("RGBA", (crop.width, max_h), (0, 0, 0, 0))
        canvas.paste(crop, (0, max_h - crop.height))  # bottom-aligned on the shared ground line
        canvas.save(out_dir / f"{name}.png")

    meta["height_px"] = int(max_h)
    (out_dir / "views.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps({"views": [c[0] for c in crops], "out": str(out_dir)}))


main()
