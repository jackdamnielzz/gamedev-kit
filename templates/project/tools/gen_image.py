"""Generate images from a recipe JSON with one of four providers: gemini, openai, nanogpt, pixellab.

Dry run by default: prints the request (attachments as file names) and a cost estimate.
Nothing is sent and nothing is billed unless you pass --run.

  python tools/gen_image.py art/recipes/explore_units_a.json            # dry run
  python tools/gen_image.py art/recipes/explore_units_a.json --estimate # estimate only
  python tools/gen_image.py art/recipes/explore_units_a.json --run      # generate

Keys come from GEMINI_API_KEY, OPENAI_API_KEY, NANOGPT_API_KEY or PIXELLAB_API_KEY and are never printed.
Outputs go to build/gen/<recipe name>[_n].png; every real call is logged to build/gen/log.jsonl
with model, cost (where the provider returns it) and a prompt hash.

Recipe fields: name, purpose (explore|reference|ui-mockup|ship), provider, model, style
("@art-direction" = the fixed paragraph from docs/specs/art-direction.md, or literal text),
prompt, refs (list of image paths), size ("1024x1024"), aspect_ratio ("16:9"), resolution
("1K"|"2K"|"4K"), quality (low|medium|high), background (transparent|opaque), n,
est_cost_usd (optional override for the estimate).

PixelLab (provider "pixellab", see docs/PIXELLAB-API.md in the kit): model is "pixen" (fast, one
image per call), "pro" (generate-image-v2: a grid of 4-64 candidates per call at small sizes) or
"pro-flash" (one high-quality image). Extra recipe fields: view (side|low top-down|high top-down),
direction (south|east|...), outline, detail, palette ("@palette" = the hex colours of
art/palette.json, or a list of hex colours), max_colors, seed. refs[0] is sent as the style image
(pro, pro-flash) at its native size; pixel-art refs are never rescaled. Estimates for PixelLab are
in subscription generations, not USD; check GET /v2/pro-flash/cost for Pro Flash prices.

Request shapes were written from the providers' docs in October 2026. The Gemini path uses
generateContent; Google documents Nano Banana 2.1 on its newer Interactions API, so verify the
first real call and adapt _gemini() if the API rejects the request.
"""
import argparse
import base64
import datetime as dt
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
GEN_DIR = ROOT / "build" / "gen"

# Rough USD per image, used only for estimates. Calibrate from the logged real costs.
PRICE_HINTS = {
    "gemini-nano-banana-2.1": 0.02,
    "gemini-3.1-flash-image": 0.034,
    "gemini-3-pro-image": 0.134,
    "gpt-image-2.5-flare": {"low": 0.006, "medium": 0.013, "high": 0.053},
    "gpt-image-2.5-sunburst": {"low": 0.006, "medium": 0.013, "high": 0.053},
    "nano-banana-2": 0.04,
    "nano-banana-pro": 0.14,
    "gpt-image-2": {"low": 0.03, "medium": 0.066, "high": 0.16},
    "openai/gpt-image-2.5/flare/text-to-image": {"low": 0.01, "medium": 0.04, "high": 0.153},
}
# PixelLab is billed in subscription generations (October 2026; Pro is 10-25 depending on size).
PIXELLAB_GENERATIONS = {"pixen": 1, "pro": 20, "pro-flash": 5}
KEY_VARS = {"gemini": "GEMINI_API_KEY", "openai": "OPENAI_API_KEY", "nanogpt": "NANOGPT_API_KEY",
            "pixellab": "PIXELLAB_API_KEY"}
PIXELLAB = "https://api.pixellab.ai/v2"


def style_paragraph(value: str) -> str:
    if value != "@art-direction":
        return value or ""
    text = (ROOT / "docs" / "specs" / "art-direction.md").read_text(encoding="utf-8")
    m = re.search(r"<!-- style:start -->(.*?)<!-- style:end -->", text, re.S)
    return m.group(1).strip() if m else ""


def ref_png(path: str, max_px=1024) -> bytes:
    """Load a reference, downscale to <= max_px, return PNG bytes (keeps uploads under ~1.5 MB)."""
    img = Image.open(ROOT / path if not Path(path).is_absolute() else path)
    img.thumbnail((max_px, max_px), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def ref_native(path: str):
    """Load a pixel-art reference at its native size (never rescaled): (png bytes, width, height)."""
    img = Image.open(ROOT / path if not Path(path).is_absolute() else path).convert("RGBA")
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return buf.getvalue(), img.width, img.height


def project_palette(value):
    """'@palette' -> hex colours from art/palette.json (its _hex block, or the linear RGB entries)."""
    if value != "@palette":
        return list(value)
    data = json.loads((ROOT / "art" / "palette.json").read_text(encoding="utf-8"))
    if isinstance(data.get("_hex"), dict):
        return list(data["_hex"].values())
    out = []
    for k, v in data.items():
        if k.startswith("_") or not isinstance(v, list):
            continue
        srgb = [(c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055) for c in v[:3]]
        out.append("#%02x%02x%02x" % tuple(max(0, min(255, round(c * 255))) for c in srgb))
    return out


def estimate(r: dict, provider: str) -> float:
    if "est_cost_usd" in r:
        return float(r["est_cost_usd"]) * int(r.get("n", 1))
    if provider == "pixellab":
        calls = 1 if r["model"] == "pro" else int(r.get("n", 1))
        return PIXELLAB_GENERATIONS.get(r["model"], float("nan")) * calls
    hint = PRICE_HINTS.get(r["model"])
    if hint is None:
        return float("nan")
    if isinstance(hint, dict):
        hint = hint.get(r.get("quality", "medium"), max(hint.values()))
    return hint * int(r.get("n", 1))


def http(url, body: bytes, headers: dict, timeout=600):
    for attempt, wait in enumerate([0, 20, 60, 120]):
        if wait:
            print(f"  retrying in {wait}s ...", file=sys.stderr)
            time.sleep(wait)
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.load(resp), dict(resp.headers)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:800]
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                print(f"  HTTP {e.code}: {detail[:200]}", file=sys.stderr)
                continue
            raise SystemExit(f"HTTP {e.code} from provider: {detail}")
    raise SystemExit("gave up after retries")


def _nanogpt(r, prompt, refs, key):
    body = {"model": r["model"], "prompt": prompt, "n": int(r.get("n", 1)), "output_format": "png"}
    if r.get("size"):
        body["resolution"] = r["size"]
    for k in ("quality", "aspect_ratio", "background", "seed"):
        if r.get(k) is not None:
            body[k] = r[k]
    if refs:
        body["input_references"] = ["data:image/png;base64," + base64.b64encode(b).decode() for b in refs]
    data, hdr = http("https://api.nano-gpt.com/api/v1/images", json.dumps(body).encode(),
                     {"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    images = []
    for item in data.get("data", []):
        if "b64_json" in item:
            images.append(base64.b64decode(item["b64_json"]))
        elif "url" in item:
            images.append(urllib.request.urlopen(item["url"], timeout=120).read())
    return images, data.get("cost"), hdr.get("X-Request-ID")


def _multipart(fields: dict, files: list):
    boundary = uuid.uuid4().hex
    out = io.BytesIO()
    for k, v in fields.items():
        out.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for name, filename, content in files:
        out.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
                  f"Content-Type: image/png\r\n\r\n".encode())
        out.write(content + b"\r\n")
    out.write(f"--{boundary}--\r\n".encode())
    return out.getvalue(), f"multipart/form-data; boundary={boundary}"


def _openai(r, prompt, refs, key):
    fields = {"model": r["model"], "prompt": prompt, "n": int(r.get("n", 1)), "output_format": "png"}
    for k in ("size", "quality", "background"):
        if r.get(k):
            fields[k] = r[k]
    auth = {"Authorization": f"Bearer {key}"}
    if refs:
        body, ctype = _multipart(fields, [("image[]", f"ref{i}.png", b) for i, b in enumerate(refs)])
        data, hdr = http("https://api.openai.com/v1/images/edits", body, {**auth, "Content-Type": ctype})
    else:
        data, hdr = http("https://api.openai.com/v1/images/generations", json.dumps(fields).encode(),
                         {**auth, "Content-Type": "application/json"})
    images = [base64.b64decode(d["b64_json"]) for d in data.get("data", []) if "b64_json" in d]
    return images, None, hdr.get("x-request-id")


def _gemini(r, prompt, refs, key):
    parts = [{"text": prompt}] + [
        {"inline_data": {"mime_type": "image/png", "data": base64.b64encode(b).decode()}} for b in refs]
    image_config = {}
    if r.get("aspect_ratio"):
        image_config["aspectRatio"] = r["aspect_ratio"]
    if r.get("resolution"):
        image_config["imageSize"] = r["resolution"]
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"], **({"imageConfig": image_config} if image_config else {})}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{r['model']}:generateContent"
    images = []
    for _ in range(int(r.get("n", 1))):
        data, _hdr = http(url, json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": key})
        for cand in data.get("candidates", []):
            for part in cand.get("content", {}).get("parts", []):
                blob = part.get("inlineData") or part.get("inline_data")
                if blob:
                    images.append(base64.b64decode(blob["data"]))
    return images, None, None


def _pixellab_images(obj) -> list:
    """Collect every base64 image object in a PixelLab response, in order."""
    found = []
    if isinstance(obj, dict):
        if isinstance(obj.get("base64"), str) and obj["base64"]:
            return [base64.b64decode(obj["base64"])]
        for v in obj.values():
            found += _pixellab_images(v)
    elif isinstance(obj, list):
        for v in obj:
            found += _pixellab_images(v)
    return found


def _pixellab_poll(job_id, key, timeout_s=1800):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        time.sleep(6)
        req = urllib.request.Request(f"{PIXELLAB}/background-jobs/{job_id}", headers={"Authorization": f"Bearer {key}"})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                job = json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code in (423, 429, 503, 529):
                continue
            raise SystemExit(f"HTTP {e.code} while polling: {e.read().decode('utf-8', 'replace')[:300]}")
        if job.get("status") == "completed":
            return job
        if job.get("status") == "failed":
            raise SystemExit(f"PixelLab job failed: {json.dumps(job.get('last_response'))[:500]}")
    raise SystemExit(f"PixelLab job {job_id} still running after {timeout_s}s; poll it later")


def _pixellab(r, prompt, refs, key):
    w, h = (int(x) for x in r.get("size", "64x64").lower().split("x"))
    model = r["model"]
    if model in ("pixen", "pro-flash") and (w % 4 or h % 4):
        raise SystemExit("PixelLab pixen / pro-flash need width and height in multiples of 4")
    body = {"description": prompt, "image_size": {"width": w, "height": h},
            "no_background": r.get("background", "transparent") == "transparent"}
    if r.get("seed") is not None:
        body["seed"] = r["seed"]
    if r.get("palette"):
        body["target_palette"] = {"colors": project_palette(r["palette"])}
        if r.get("max_colors"):
            body["target_palette"]["max_colors"] = r["max_colors"]
    ref_objs = [{"image": {"type": "base64", "base64": base64.b64encode(b).decode(), "format": "png"},
                 "size": {"width": rw, "height": rh}} for b, rw, rh in refs]

    if model == "pixen":
        for k in ("outline", "detail", "view", "direction"):
            if r.get(k):
                body[k] = r[k]
        path, calls = "/create-image-pixen", int(r.get("n", 1))
    elif model == "pro":
        path, calls = "/generate-image-v2", 1
        if ref_objs:
            body["style_image"] = ref_objs[0]
            if ref_objs[1:]:
                body["reference_images"] = ref_objs[1:5]
    elif model == "pro-flash":
        path, calls = "/create-image-pro-flash", int(r.get("n", 1))
        if ref_objs:
            body["style_image"] = ref_objs[0]
    else:
        raise SystemExit("pixellab model must be pixen, pro or pro-flash")
    if "style_image" in body and "target_palette" in body:
        body["style_options"] = {"color_palette": False, "outline": True, "detail": True, "shading": True}

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
    images, generations, job_ids = [], 0.0, []
    for _ in range(calls):
        data, _hdr = http(PIXELLAB + path, json.dumps(body).encode(), headers)
        if data.get("background_job_id"):
            job_ids.append(data["background_job_id"])
            data = _pixellab_poll(data["background_job_id"], key)
            images += _pixellab_images(data.get("last_response"))
        else:
            images += _pixellab_images(data.get("image"))
        usage = data.get("usage") or {}
        generations += float(usage.get("generations") or 0)
    return images, {"type": "generations", "generations": generations}, ",".join(job_ids) or None


PROVIDERS = {"nanogpt": _nanogpt, "openai": _openai, "gemini": _gemini, "pixellab": _pixellab}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("recipe")
    p.add_argument("--run", action="store_true", help="actually call the provider (costs money)")
    p.add_argument("--estimate", action="store_true", help="print only the cost estimate")
    p.add_argument("--provider", choices=list(PROVIDERS), help="override the recipe's provider")
    a = p.parse_args()

    r = json.loads(Path(a.recipe).read_text(encoding="utf-8"))
    provider = a.provider or r.get("provider", "gemini")
    prompt = "\n".join(x for x in (style_paragraph(r.get("style", "")), r["prompt"]) if x)
    est = estimate(r, provider)
    est_key = "estimate_generations" if provider == "pixellab" else "estimate_usd"

    if a.estimate:
        print(json.dumps({"recipe": r["name"], "model": r["model"], est_key: est}))
        return

    preview = {"provider": provider, "model": r["model"], "purpose": r.get("purpose"), "prompt": prompt,
               "refs": r.get("refs", []), "n": r.get("n", 1),
               **{k: r[k] for k in ("size", "aspect_ratio", "resolution", "quality", "background",
                                    "view", "direction", "outline", "detail", "palette", "seed") if k in r},
               est_key: est}
    if not a.run:
        print(json.dumps(preview, indent=2))
        print("dry run: nothing sent. Add --run to generate.")
        return

    key = os.environ.get(KEY_VARS[provider])
    if not key:
        raise SystemExit(f"{KEY_VARS[provider]} is not set")

    load_ref = ref_native if provider == "pixellab" else ref_png
    refs = [load_ref(x) for x in r.get("refs", [])]
    images, cost, request_id = PROVIDERS[provider](r, prompt, refs, key)
    if not images:
        raise SystemExit("provider returned no images")

    GEN_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for i, data in enumerate(images):
        out = GEN_DIR / (f"{r['name']}.png" if len(images) == 1 else f"{r['name']}_{i + 1}.png")
        out.write_bytes(data)
        written.append(str(out.relative_to(ROOT)))

    entry = {"date": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "recipe": a.recipe,
             "name": r["name"], "purpose": r.get("purpose"), "provider": provider, "model": r["model"],
             "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest()[:16], "refs": r.get("refs", []),
             "outputs": written, est_key: est, "request_id": request_id}
    entry["usage" if isinstance(cost, dict) else "cost_usd"] = cost
    with open(GEN_DIR / "log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps({"outputs": written, "usage" if isinstance(cost, dict) else "cost_usd": cost, est_key: est}))


main()
