#!/usr/bin/env python3
"""Turn an AI-generated animation video (flat key-colour background) into clean,
grid-true pixel-art frames that share ONE crop box, ONE pixel grid and ONE palette.

    python art/py/video_to_sprites.py in.mp4 --out build/art/punch --height 64 --colors 24 --fps 12
    python art/py/video_to_sprites.py in.mp4 --out build/art/punch --height 64 --palette art/palette.json

Why one of everything: if each frame is snapped on its own, the grid offset, scale
and palette drift between frames and the sprite flickers and "breathes" in game.

Steps
  1. ffmpeg extracts frames at --fps (optionally --start/--end seconds)
  2. key out the background (colour sampled from the frame borders, or --key #00ff00),
     despill, binary alpha; --drop-shadow also removes cast shadows on the screen
  3. one shared crop box = union of the subject over all frames (+ margin)
  4. one shared scale = crop height / --height; every frame is downsampled with the
     same grid: dominant colour per cell, alpha by majority
  5. one shared palette: k-means in Oklab over all frames (--colors), or a fixed
     --palette (json list of hex, or {name: [r,g,b] 0-1 linear} as written by
     extract_palette.py); mapped by nearest colour, no dithering
  6. cleanup: orphan pixels removed, optional 1-px selective outline (--outline)
  7. report: colours used, pixels changed between consecutive frames, bbox jitter
  8. writes frames/NNN.png, sheet.png + sheet.json, preview.gif (x4, nearest) and
     compare.png (raw frame vs result) for the human / agent to inspect

After this, run the sheet through Sprite Grid for hand touch-up (dithering OFF, no
retro palette), then re-run the lint (--lint-only) so nothing off-palette slips in.
Requires: ffmpeg on PATH, numpy, Pillow.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image


# --------------------------------------------------------------------------- colour
def srgb_to_lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055) * 255.0


def to_oklab(rgb):
    """rgb uint8-ish array (..., 3) -> Oklab (..., 3)"""
    l = srgb_to_lin(rgb.astype(np.float64))
    m1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                   [0.2119034982, 0.6806995451, 0.1073969566],
                   [0.0883024619, 0.2817188376, 0.6299787005]])
    lms = np.cbrt(l @ m1.T)
    m2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                   [1.9779984951, -2.4285922050, 0.4505937099],
                   [0.0259040371, 0.7827717662, -0.8086757660]])
    return lms @ m2.T


def nearest(lab, pal_lab):
    d = ((lab[:, None, :] - pal_lab[None, :, :]) ** 2).sum(-1)
    return d.argmin(1)


def kmeans(lab, k, iters=25, seed=1):
    rng = np.random.default_rng(seed)
    # k-means++ init
    c = [lab[rng.integers(len(lab))]]
    for _ in range(1, k):
        d = np.min(((lab[:, None] - np.array(c)[None]) ** 2).sum(-1), 1)
        c.append(lab[rng.choice(len(lab), p=d / d.sum())])
    c = np.array(c)
    for _ in range(iters):
        a = nearest(lab, c)
        for j in range(k):
            m = lab[a == j]
            if len(m):
                c[j] = m.mean(0)
    return c


def load_palette(path: Path):
    data = json.loads(path.read_text())
    cols = []
    if isinstance(data, dict):
        for v in data.values():
            v = np.array(v, dtype=float)
            cols.append(lin_to_srgb(v) if v.max() <= 1.0 else v)
    else:
        for h in data:
            h = h.lstrip('#')
            cols.append([int(h[i:i + 2], 16) for i in (0, 2, 4)])
    return np.clip(np.array(cols, dtype=float), 0, 255)


# --------------------------------------------------------------------------- steps
def extract_frames(video: Path, fps: float, start, end, tmp: Path):
    if not shutil.which('ffmpeg'):
        sys.exit('ffmpeg not found on PATH')
    cmd = ['ffmpeg', '-loglevel', 'error', '-y']
    if start is not None:
        cmd += ['-ss', str(start)]
    if end is not None:
        cmd += ['-to', str(end)]
    cmd += ['-i', str(video), '-vf', f'fps={fps}', str(tmp / 'f_%04d.png')]
    subprocess.run(cmd, check=True)
    files = sorted(tmp.glob('f_*.png'))
    if not files:
        sys.exit('no frames extracted')
    return [np.array(Image.open(f).convert('RGB')) for f in files]


def key_colour(frames):
    border = np.concatenate([np.concatenate([f[:4].reshape(-1, 3), f[-4:].reshape(-1, 3),
                                             f[:, :4].reshape(-1, 3), f[:, -4:].reshape(-1, 3)]) for f in frames[:5]])
    return np.median(border, 0)


def key_out(frame, key, tol, drop_shadow=False):
    lab = to_oklab(frame.reshape(-1, 3).astype(float))
    klab = to_oklab(key[None].astype(float))[0]
    # chroma distance dominates; lightness counts a little
    d = np.sqrt(((lab[:, 1:] - klab[1:]) ** 2).sum(1) + 0.25 * (lab[:, 0] - klab[0]) ** 2)
    bg = d <= tol
    if drop_shadow:
        # cast shadows on a green screen are darker pixels with the key's hue: treat as background.
        # (Anything green on the subject goes too; that is the price of green screens.)
        kc = np.hypot(klab[1], klab[2])
        c = np.hypot(lab[:, 1], lab[:, 2])
        cosang = (lab[:, 1] * klab[1] + lab[:, 2] * klab[2]) / np.maximum(c * kc, 1e-9)
        bg |= (cosang > 0.9) & (c > kc * 0.25) & (lab[:, 0] < klab[0])
    alpha = (~bg).reshape(frame.shape[:2])
    out = frame.astype(float).copy()
    # despill: the key channel may not exceed the average of the other two
    ki = int(np.argmax(key))
    others = [i for i in range(3) if i != ki]
    lim = out[..., others].mean(-1)
    out[..., ki] = np.minimum(out[..., ki], lim + 8)
    # erode alpha by one pixel to drop the key-tinted fringe
    a = alpha.copy()
    a[1:-1, 1:-1] &= alpha[:-2, 1:-1] & alpha[2:, 1:-1] & alpha[1:-1, :-2] & alpha[1:-1, 2:]
    return out, a


def downsample(rgb, alpha, box, scale, ow, oh):
    x0, y0 = box
    out = np.zeros((oh, ow, 3))
    oa = np.zeros((oh, ow), bool)
    for j in range(oh):
        for i in range(ow):
            ys, ye = int(round(y0 + j * scale)), int(round(y0 + (j + 1) * scale))
            xs, xe = int(round(x0 + i * scale)), int(round(x0 + (i + 1) * scale))
            ca = alpha[ys:ye, xs:xe]
            if ca.size == 0 or ca.mean() < 0.5:
                continue
            px = rgb[ys:ye, xs:xe][ca]
            # dominant colour: most common after coarse binning; mean of that bin
            q = (px // 24).astype(int)
            keys = q[:, 0] * 10000 + q[:, 1] * 100 + q[:, 2]
            vals, counts = np.unique(keys, return_counts=True)
            top = vals[counts.argmax()]
            out[j, i] = px[keys == top].mean(0)
            oa[j, i] = True
    return out, oa


def clean_orphans(idx, alpha):
    """A pixel whose 4 neighbours all share one other colour takes that colour."""
    h, w = idx.shape
    res = idx.copy()
    for y in range(h):
        for x in range(w):
            if not alpha[y, x]:
                continue
            nb = [idx[yy, xx] for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                  if 0 <= yy < h and 0 <= xx < w and alpha[yy, xx]]
            if len(nb) >= 3 and idx[y, x] not in nb and len(set(nb)) == 1:
                res[y, x] = nb[0]
    # single opaque pixels with no opaque neighbour are dropped
    a = alpha.copy()
    pad = np.pad(alpha, 1)
    n = pad[:-2, 1:-1].astype(int) + pad[2:, 1:-1] + pad[1:-1, :-2] + pad[1:-1, 2:]
    a[(n == 0)] = False
    return res, a


def add_outline(idx, alpha, pal_lab):
    """1-px selective outline outside the silhouette: darkest palette colour close in hue
    to the neighbouring edge pixel."""
    h, w = idx.shape
    darkest = int(pal_lab[:, 0].argmin())
    pad_a = np.pad(alpha, 1)
    ring = (~alpha) & (pad_a[:-2, 1:-1] | pad_a[2:, 1:-1] | pad_a[1:-1, :-2] | pad_a[1:-1, 2:])
    out = idx.copy()
    for y, x in zip(*np.nonzero(ring)):
        for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= yy < h and 0 <= xx < w and alpha[yy, xx]:
                src = pal_lab[idx[yy, xx]]
                cand = [k for k in range(len(pal_lab)) if pal_lab[k, 0] < src[0] - 0.12]
                out[y, x] = min(cand, key=lambda k: ((pal_lab[k, 1:] - src[1:]) ** 2).sum() + 0.3 * pal_lab[k, 0]) if cand else darkest
                break
    return out, alpha | ring


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('video', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--fps', type=float, default=12)
    ap.add_argument('--start', type=float)
    ap.add_argument('--end', type=float)
    ap.add_argument('--height', type=int, default=64, help='sprite height in pixels (sets the shared grid)')
    ap.add_argument('--colors', type=int, default=24)
    ap.add_argument('--palette', type=Path, help='fixed palette json; overrides --colors')
    ap.add_argument('--key', help='background colour, e.g. #00ff00 (default: sampled from borders)')
    ap.add_argument('--tol', type=float, default=0.12, help='key tolerance in Oklab units')
    ap.add_argument('--margin', type=int, default=2, help='transparent margin in output pixels')
    ap.add_argument('--outline', action='store_true')
    ap.add_argument('--drop-shadow', action='store_true', help='also key out darker key-hued pixels (cast shadows)')
    ap.add_argument('--every', type=int, default=1, help='keep every Nth extracted frame')
    a = ap.parse_args()

    a.out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        raw = extract_frames(a.video, a.fps, a.start, a.end, Path(td))[::a.every]
    key = np.array([int(a.key.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)], float) if a.key else key_colour(raw)
    keyed = [key_out(f, key, a.tol, a.drop_shadow) for f in raw]

    # shared crop box over all frames
    union = np.zeros(raw[0].shape[:2], bool)
    for _, al in keyed:
        union |= al
    ys, xs = np.nonzero(union)
    if not len(ys):
        sys.exit('nothing left after keying: try a larger --tol or set --key')
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    scale = (y1 - y0) / (a.height - 2 * a.margin)
    m = a.margin * scale
    bx, by = x0 - m, y0 - m
    ow = int(np.ceil((x1 - x0 + 2 * m) / scale))
    oh = a.height
    H, W = raw[0].shape[:2]
    padw = int(np.ceil(m)) + 2
    small = []
    for rgb, al in keyed:
        rgbp = np.pad(rgb, ((padw, padw), (padw, padw), (0, 0)), mode='edge')
        alp = np.pad(al, padw)
        small.append(downsample(rgbp, alp, (bx + padw, by + padw), scale, ow, oh))

    # shared palette
    opaque = np.concatenate([s[0][s[1]] for s in small])
    lab_all = to_oklab(opaque)
    if a.palette:
        pal_rgb = load_palette(a.palette)
        pal_lab = to_oklab(pal_rgb)
    else:
        sample = lab_all[np.random.default_rng(0).choice(len(lab_all), min(len(lab_all), 20000), replace=False)]
        pal_lab = kmeans(sample, min(a.colors, len(sample)))
        # back to sRGB through the mean of the member pixels
        assign = nearest(lab_all, pal_lab)
        pal_rgb = np.array([opaque[assign == k].mean(0) if (assign == k).any() else [0, 0, 0] for k in range(len(pal_lab))])
        pal_rgb = np.round(pal_rgb)
        pal_lab = to_oklab(pal_rgb)

    frames, report = [], []
    prev = None
    for n, (rgb, al) in enumerate(small):
        idx = np.zeros(al.shape, int)
        idx[al] = nearest(to_oklab(rgb[al]), pal_lab)
        idx, al = clean_orphans(idx, al)
        if a.outline:
            idx, al = add_outline(idx, al, pal_lab)
        img = np.zeros((oh, ow, 4), np.uint8)
        img[..., :3] = pal_rgb[idx].astype(np.uint8)
        img[..., 3] = np.where(al, 255, 0)
        frames.append(img)
        yy, xx = np.nonzero(al)
        bbox = (int(xx.min()), int(yy.min()), int(xx.max()), int(yy.max())) if len(yy) else None
        changed = None
        if prev is not None:
            changed = round(float((np.any(prev != img, -1)).mean()) * 100, 1)
        report.append({'frame': n, 'opaque_px': int(al.sum()), 'bbox': bbox, 'changed_vs_prev_pct': changed})
        prev = img

    # outputs
    fdir = a.out / 'frames'
    fdir.mkdir(exist_ok=True)
    for n, f in enumerate(frames):
        Image.fromarray(f).save(fdir / f'{n:03d}.png')
    cols = min(len(frames), 10)
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols * ow, rows * oh))
    for n, f in enumerate(frames):
        sheet.paste(Image.fromarray(f), ((n % cols) * ow, (n // cols) * oh))
    sheet.save(a.out / 'sheet.png')
    used = sorted({tuple(int(v) for v in c) for f in frames for c in f[f[..., 3] > 0][:, :3]})
    meta = {'source': a.video.name, 'frame_w': ow, 'frame_h': oh, 'cols': cols, 'rows': rows, 'frames': len(frames),
            'fps': a.fps / a.every, 'scale_src_px_per_px': round(scale, 3), 'key': [int(v) for v in key],
            'palette': ['#%02x%02x%02x' % tuple(int(v) for v in c) for c in pal_rgb], 'colours_used': len(used),
            'report': report}
    (a.out / 'sheet.json').write_text(json.dumps(meta, indent=1))

    big = [Image.fromarray(f).resize((ow * 4, oh * 4), Image.NEAREST) for f in frames]
    bg = [Image.new('RGBA', b.size, (38, 44, 52, 255)) for b in big]
    gif = [Image.alpha_composite(g, b).convert('P', palette=Image.ADAPTIVE) for g, b in zip(bg, big)]
    gif[0].save(a.out / 'preview.gif', save_all=True, append_images=gif[1:], duration=int(1000 * a.every / a.fps), loop=0, disposal=2)

    # compare: raw frame (scaled to same height) next to the result, for 4 frames
    picks = np.linspace(0, len(frames) - 1, min(4, len(frames))).astype(int)
    tiles = []
    for p in picks:
        r = Image.fromarray(raw[p][int(max(0, y0)):int(y1), int(max(0, x0)):int(x1)])
        r = r.resize((int(r.width * oh * 4 / r.height), oh * 4), Image.LANCZOS).convert('RGBA')
        s = Image.alpha_composite(Image.new('RGBA', (ow * 4, oh * 4), (38, 44, 52, 255)), big[p])
        t = Image.new('RGBA', (r.width + s.width + 8, oh * 4), (20, 20, 20, 255))
        t.paste(r, (0, 0)); t.paste(s, (r.width + 8, 0))
        tiles.append(t)
    cw = max(t.width for t in tiles)
    comp = Image.new('RGBA', (cw, len(tiles) * (oh * 4 + 6)), (20, 20, 20, 255))
    for n, t in enumerate(tiles):
        comp.paste(t, (0, n * (oh * 4 + 6)))
    comp.save(a.out / 'compare.png')

    ch = [r['changed_vs_prev_pct'] for r in report if r['changed_vs_prev_pct'] is not None]
    hs = [r['bbox'][3] - r['bbox'][1] for r in report if r['bbox']]
    print(f'{len(frames)} frames of {ow}x{oh}px, scale {scale:.2f} src px per px, {len(used)} colours used')
    if ch:
        print(f'pixels changed between frames: median {np.median(ch):.1f}%, max {max(ch):.1f}%')
    if hs:
        print(f'subject height range: {min(hs)}-{max(hs)} px')
    print('wrote', a.out / 'sheet.png', a.out / 'preview.gif', a.out / 'compare.png')


if __name__ == '__main__':
    main()
