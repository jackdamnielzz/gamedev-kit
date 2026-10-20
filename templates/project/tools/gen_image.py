"""Generate images from a recipe JSON with one of three providers: gemini, openai, nanogpt.

Dry run by default: prints the request (attachments as file names) and a cost estimate.
Nothing is sent and nothing is billed unless you pass --run.

  python tools/gen_image.py art/recipes/explore_units_a.json            # dry run
  python tools/gen_image.py art/recipes/explore_units_a.json --estimate # estimate only
  python tools/gen_image.py art/recipes/explore_units_a.json --run      # generate

Keys come from GEMINI_API_KEY, OPENAI_API_KEY or NANOGPT_API_KEY and are never printed.
Outputs go to build/gen/<recipe name>[_n].png; every real call is logged to build/gen/log.jsonl
with model, cost (where the provider returns it) and a prompt hash.

Recipe fields: name, purpose (explore|reference|ui-mockup|ship), provider, model, style
("@art-direction" = the fixed paragraph from docs/specs/art-direction.md, or literal text),
prompt, refs (list of image paths), size ("1024x1024"), aspect_ratio ("16:9"), resolution
("1K"|"2K"|"4K"), quality (low|medium|high), background (transparent|opaque), n,
est_cost_usd (optional override for the estimate).

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
KEY_VARS = {"gemini": "GEMINI_API_KEY", "openai": "OPENAI_API_KEY", "nanogpt": "NANOGPT_API_KEY"}


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


def estimate(r: dict) -> float:
    if "est_cost_usd" in r:
        return float(r["est_cost_usd"]) * int(r.get("n", 1))
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


PROVIDERS = {"nanogpt": _nanogpt, "openai": _openai, "gemini": _gemini}


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
    est = estimate(r)

    if a.estimate:
        print(json.dumps({"recipe": r["name"], "model": r["model"], "estimate_usd": est}))
        return

    preview = {"provider": provider, "model": r["model"], "purpose": r.get("purpose"), "prompt": prompt,
               "refs": r.get("refs", []), "n": r.get("n", 1),
               **{k: r[k] for k in ("size", "aspect_ratio", "resolution", "quality", "background") if k in r},
               "estimate_usd": est}
    if not a.run:
        print(json.dumps(preview, indent=2))
        print("dry run: nothing sent. Add --run to generate.")
        return

    key = os.environ.get(KEY_VARS[provider])
    if not key:
        raise SystemExit(f"{KEY_VARS[provider]} is not set")

    refs = [ref_png(x) for x in r.get("refs", [])]
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
             "outputs": written, "cost_usd": cost, "estimate_usd": est, "request_id": request_id}
    with open(GEN_DIR / "log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps({"outputs": written, "cost_usd": cost, "estimate_usd": est}))


main()
