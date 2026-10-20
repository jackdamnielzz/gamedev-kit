import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def silhouette_from_reference(img: Image.Image, tol: int = 30) -> np.ndarray:
    rgba = np.asarray(img.convert("RGBA"))
    if (rgba[:, :, 3] < 255).any():          # sliced views from slice_refs.py are transparent
        return rgba[:, :, 3] > 10
    a = rgba[:, :, :3].astype(int)
    bg = np.median(np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]), axis=0)
    return np.abs(a - bg).sum(axis=2) > tol


def silhouette_from_render(img: Image.Image) -> np.ndarray:
    return np.asarray(img.convert("RGBA"))[:, :, 3] > 10


def crop_to(mask: np.ndarray, img: Image.Image, height: int):
    ys, xs = np.nonzero(mask)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    c_img = img.crop(box)
    c_mask = Image.fromarray(mask[box[1]:box[3], box[0]:box[2]].astype(np.uint8) * 255)
    w = round(c_img.width * height / c_img.height)
    return c_img.resize((w, height), Image.LANCZOS), c_mask.resize((w, height), Image.NEAREST)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ref", required=True)
    p.add_argument("--render", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--height", type=int, default=512)
    a = p.parse_args()

    ref, ren = Image.open(a.ref), Image.open(a.render)
    ref_img, ref_m = crop_to(silhouette_from_reference(ref), ref, a.height)
    ren_img, ren_m = crop_to(silhouette_from_render(ren), ren, a.height)

    w = max(ref_m.width, ren_m.width)
    rm = np.zeros((a.height, w), bool)
    nm = np.zeros((a.height, w), bool)
    rm[:, (w - ref_m.width) // 2:(w - ref_m.width) // 2 + ref_m.width] = np.asarray(ref_m) > 0
    nm[:, (w - ren_m.width) // 2:(w - ren_m.width) // 2 + ren_m.width] = np.asarray(ren_m) > 0
    iou = float((rm & nm).sum() / max((rm | nm).sum(), 1))

    overlay = np.full((a.height, w, 3), 255, np.uint8)
    overlay[rm & ~nm] = (230, 60, 60)    # only in reference: missing in the build
    overlay[nm & ~rm] = (60, 110, 230)   # only in render: extra in the build
    overlay[rm & nm] = (90, 90, 90)      # match

    sheet = Image.new("RGB", (ref_img.width + ren_img.width + w + 40, a.height), "white")
    sheet.paste(ref_img.convert("RGB"), (0, 0))
    sheet.paste(ren_img.convert("RGBA"), (ref_img.width + 20, 0), ren_img.convert("RGBA"))
    sheet.paste(Image.fromarray(overlay), (ref_img.width + ren_img.width + 40, 0))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(a.out)
    print(json.dumps({"silhouette_iou": round(iou, 3), "out": a.out}))


main()
