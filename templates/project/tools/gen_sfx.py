"""Generate sound effects from a recipe JSON with ElevenLabs Sound Effects, direct or through NanoGPT.

Dry run by default: prints the request and a cost estimate. Nothing is sent or billed without --run.

  python tools/gen_sfx.py audio/sfx/recipes/unit_died.json            # dry run
  python tools/gen_sfx.py audio/sfx/recipes/unit_died.json --run      # generate

Recipe fields: name (use the sim event, e.g. "unit_died"), provider ("elevenlabs" | "nanogpt"),
prompt, duration_seconds (0.5-30), prompt_influence (0-1), loop (true for ambience), n (3-5
variants for the human to pick from), model_id (optional), output_format (optional, ElevenLabs,
default "mp3_44100_128"), model (NanoGPT, default "elevenlabs/sound-effects/v2").

Keys: ELEVENLABS_API_KEY or NANOGPT_API_KEY, never printed. Ship from a paid ElevenLabs plan;
NanoGPT is for prototypes (AI-ASSET-WORKFLOW.md, "Sound effects"). Outputs go to
build/gen/sfx/<name>_<i>.<ext>; with ffmpeg on the PATH each file also gets a spectrogram PNG and a
loudness JSON for review, because an agent cannot listen. Every real call is logged to
build/gen/log.jsonl. Request shapes follow the providers' docs of October 2026: check the first
real call and adapt if the API rejects it.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "build" / "gen" / "sfx"
LOG = ROOT / "build" / "gen" / "log.jsonl"
KEY_VARS = {"elevenlabs": "ELEVENLABS_API_KEY", "nanogpt": "NANOGPT_API_KEY"}
# Rough USD per second of audio, for estimates only (October 2026). Calibrate on real costs.
USD_PER_SECOND = {"elevenlabs": 0.12 / 60, "nanogpt": 0.002}


def post(url: str, body: dict, headers: dict) -> tuple[bytes, dict]:
    data = json.dumps(body).encode()
    for attempt, wait in enumerate([0, 20, 60, 120]):
        if wait:
            print(f"  retrying in {wait}s ...", file=sys.stderr)
            time.sleep(wait)
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **headers}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                return resp.read(), dict(resp.headers)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:600]
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                print(f"  HTTP {e.code}: {detail[:200]}", file=sys.stderr)
                continue
            raise SystemExit(f"HTTP {e.code} from provider: {detail}")
    raise SystemExit("gave up after retries")


def request(r: dict, provider: str) -> tuple[str, dict, dict]:
    if provider == "elevenlabs":
        fmt = r.get("output_format", "mp3_44100_128")
        body = {"text": r["prompt"], "duration_seconds": r.get("duration_seconds"),
                "prompt_influence": r.get("prompt_influence", 0.3), "loop": bool(r.get("loop", False))}
        if r.get("model_id"):
            body["model_id"] = r["model_id"]
        return f"https://api.elevenlabs.io/v1/sound-generation?output_format={fmt}", body, {"xi-api-key": "<key>"}
    body = {"model": r.get("model", "elevenlabs/sound-effects/v2"), "input": r["prompt"], "voice": "none"}
    for k in ("duration_seconds", "prompt_influence", "loop"):
        if k in r:
            body[k] = r[k]
    return "https://api.nano-gpt.com/api/v1/audio/speech", body, {"Authorization": "Bearer <key>"}


def extension(headers: dict, r: dict) -> str:
    ctype = {k.lower(): v for k, v in headers.items()}.get("content-type", "")
    for token, ext in (("wav", "wav"), ("ogg", "ogg"), ("opus", "opus"), ("mpeg", "mp3"), ("mp3", "mp3")):
        if token in ctype:
            return ext
    fmt = r.get("output_format", "mp3")
    return "wav" if fmt.startswith(("pcm", "wav")) else "mp3"


def review_files(path: Path) -> dict:
    """Spectrogram PNG + loudness numbers, so the agent can check clipping and level."""
    if not shutil.which("ffmpeg"):
        return {}
    png = path.with_suffix(".spectrogram.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(path), "-lavfi", "showspectrumpic=s=800x300", str(png)], check=False)
    p = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True, check=False)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p.stderr, re.S)
    loudness = json.loads(m.group(0)) if m else {}
    path.with_suffix(".loudness.json").write_text(json.dumps(loudness, indent=2), encoding="utf-8")
    return {"spectrogram": str(png.relative_to(ROOT)), "input_lufs": loudness.get("input_i"), "true_peak_db": loudness.get("input_tp")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("recipe")
    ap.add_argument("--run", action="store_true", help="actually call the provider (costs money)")
    a = ap.parse_args()

    r = json.loads(Path(a.recipe).read_text(encoding="utf-8"))
    provider = r.get("provider", "elevenlabs")
    if provider not in KEY_VARS:
        raise SystemExit(f"provider must be one of {list(KEY_VARS)}")
    n = int(r.get("n", 3))
    est = round(USD_PER_SECOND[provider] * float(r.get("duration_seconds") or 5) * n, 4)
    url, body, shown_headers = request(r, provider)

    if not a.run:
        print(json.dumps({"provider": provider, "url": url, "body": body, "headers": shown_headers, "n": n, "estimate_usd": est}, indent=2))
        print("dry run: nothing sent. Add --run to generate.")
        return

    key = os.environ.get(KEY_VARS[provider])
    if not key:
        raise SystemExit(f"{KEY_VARS[provider]} is not set")
    headers = {"xi-api-key": key} if provider == "elevenlabs" else {"Authorization": f"Bearer {key}"}

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for i in range(1, n + 1):
        audio, resp_headers = post(url, body, headers)
        out = OUT_DIR / f"{r['name']}_{i}.{extension(resp_headers, r)}"
        out.write_bytes(audio)
        outputs.append({"file": str(out.relative_to(ROOT)), **review_files(out)})

    entry = {"date": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "recipe": a.recipe, "name": r["name"],
             "kind": "sfx", "provider": provider, "model": body.get("model") or body.get("model_id") or "elevenlabs-sound-effects",
             "prompt_hash": hashlib.sha256(r["prompt"].encode()).hexdigest()[:16], "outputs": [o["file"] for o in outputs],
             "estimate_usd": est}
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps({"outputs": outputs, "estimate_usd": est}, indent=2))


if __name__ == "__main__":
    main()
