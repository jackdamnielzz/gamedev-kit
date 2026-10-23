"""PIXEL ART ONLY. Small shared PixelLab v2 client for the tools in tools/pixellab/.

Everything that talks to https://api.pixellab.ai/v2 goes through here: auth from PIXELLAB_API_KEY
(never printed), retries with Retry-After, polling, downloads, balance checks and the
append-only generation log. See docs/PIXELLAB-API.md in the gamedev-kit for the API itself.
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

API = "https://api.pixellab.ai/v2"
ROOT = Path(__file__).resolve().parents[2]
GEN_DIR = ROOT / "build" / "gen"
PREVIEW_DIR = ROOT / "build" / "previews"
LOG = GEN_DIR / "log.jsonl"
DIRECTIONS = ["south", "south-east", "east", "north-east", "north", "north-west", "west", "south-west"]
RETRY_CODES = {408, 429, 500, 502, 503, 504, 529}
DONE = {"completed", "complete", "succeeded", "success", "done"}
FAILED = {"failed", "error", "cancelled", "canceled"}


class PixelLabError(RuntimeError):
    def __init__(self, status: int, detail: str):
        super().__init__(f"HTTP {status}: {detail}")
        self.status = status
        self.detail = detail


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


class Client:
    def __init__(self, key: str | None = None, timeout: int = 300):
        self.key = key or os.environ.get("PIXELLAB_API_KEY")
        if not self.key:
            raise SystemExit("PIXELLAB_API_KEY is not set (user environment variable).")
        self.timeout = timeout

    def request(self, method: str, path: str, body: dict | None = None, retries: int = 4) -> dict:
        data = json.dumps(body).encode() if body is not None else None
        for attempt in range(retries + 1):
            req = urllib.request.Request(API + path, data=data, method=method, headers={
                "Authorization": f"Bearer {self.key}", "Content-Type": "application/json",
                "User-Agent": "gamedev-kit-pixellab/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    raw = r.read()
                    return json.loads(raw) if raw else {}
            except urllib.error.HTTPError as e:
                detail = e.read().decode("utf-8", "replace")[:600]
                if e.code in RETRY_CODES and attempt < retries:
                    wait = int(e.headers.get("Retry-After") or (15 * 2 ** attempt))
                    log(f"  HTTP {e.code}, retrying in {wait}s")
                    time.sleep(min(wait, 180))
                    continue
                raise PixelLabError(e.code, detail) from None
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt < retries:
                    log(f"  network error ({e}), retrying in 15s")
                    time.sleep(15)
                    continue
                raise
        raise PixelLabError(0, "gave up after retries")

    def get(self, path: str) -> dict:
        return self.request("GET", path)

    def post(self, path: str, body: dict) -> dict:
        return self.request("POST", path, body, retries=2)  # few retries: a POST may already be billed

    def generations_left(self) -> float:
        b = self.get("/balance")
        return float((b.get("subscription") or {}).get("generations") or 0)

    def wait_for(self, path: str, label: str, every: int = 8, timeout_s: int = 1800) -> dict:
        """Poll GET path until status is done or failed. 423 / 404-while-starting count as 'still running'."""
        start, last = time.time(), None
        while time.time() - start < timeout_s:
            try:
                info = self.get(path)
            except PixelLabError as e:
                if e.status in (404, 423):
                    info = {"status": "processing"}
                else:
                    raise
            status = str(info.get("status", "")).lower()
            extra = info.get("last_response") or {}
            queue = extra.get("queue_position") if isinstance(extra, dict) else None
            shown = f"{status}" + (f", queue {queue}" if queue is not None else "")
            if shown != last:
                log(f"  {label}: {shown} ({int(time.time() - start)}s)")
                last = shown
            if status in DONE:
                return info
            if status in FAILED:
                raise PixelLabError(0, f"{label} failed: {json.dumps(info)[:400]}")
            time.sleep(every)
        raise TimeoutError(f"{label} not finished after {timeout_s}s; it may still finish, resume later")

    def download(self, url: str) -> bytes:
        # The file host refuses Python's default User-Agent (403).
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (gamedev-kit)"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    return r.read()
            except urllib.error.URLError:
                if attempt == 3:
                    raise
                time.sleep(5 * (attempt + 1))
        return b""


def image_payload(path: Path) -> dict:
    return {"type": "base64", "format": "png", "base64": base64.b64encode(path.read_bytes()).decode()}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sprite_stats(img: Image.Image) -> dict:
    """Opaque bounding box, height and colour count of an RGBA sprite."""
    alpha = img.getchannel("A")
    box = alpha.point(lambda a: 255 if a > 0 else 0).getbbox()
    colours = {px[:3] for px in img.getdata() if px[3] > 0}
    return {"bbox": list(box) if box else None, "height": (box[3] - box[1]) if box else 0,
            "width": (box[2] - box[0]) if box else 0, "colours": len(colours),
            "semi_transparent": sum(1 for a in alpha.getdata() if 0 < a < 255)}


def append_log(entry: dict) -> None:
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    entry = {"date": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), **entry}
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def add_to_manifest(entries: list[dict]) -> bool:
    """Append entries to assets/manifest.json if the project has one. Returns True when written."""
    path = ROOT / "assets" / "manifest.json"
    if not path.exists():
        return False
    data = json.loads(path.read_text(encoding="utf-8"))
    known = {e.get("path") for e in data.get("entries", [])}
    data.setdefault("entries", []).extend(e for e in entries if e["path"] not in known)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return True


def labelled_sheet(frames: list[tuple[str, Image.Image]], out: Path, scale: int = 4) -> None:
    """Nearest-neighbour preview on mid-grey with the direction name under each frame."""
    from PIL import ImageDraw, ImageFont
    w = max(f.width for _, f in frames) * scale
    h = max(f.height for _, f in frames) * scale
    label_h, gap = 16, 8
    sheet = Image.new("RGBA", (len(frames) * (w + gap) - gap, h + label_h), (128, 128, 128, 255))
    draw, font = ImageDraw.Draw(sheet), ImageFont.load_default()
    for i, (name, f) in enumerate(frames):
        x = i * (w + gap)
        sheet.alpha_composite(f.resize((f.width * scale, f.height * scale), Image.NEAREST), (x, 0))
        draw.text((x + 4, h + 2), name, fill=(20, 20, 20, 255), font=font)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)


def spritesheet(frames: list[tuple[str, Image.Image]], png: Path, meta: Path) -> None:
    """One row of equal cells (never rescaled), plus a JSON map direction -> cell."""
    w = max(f.width for _, f in frames)
    h = max(f.height for _, f in frames)
    sheet = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    layout = {}
    for i, (name, f) in enumerate(frames):
        x = i * w + (w - f.width) // 2
        sheet.alpha_composite(f, (x, h - f.height))
        layout[name] = {"x": i * w, "y": 0, "w": w, "h": h}
    sheet.save(png)
    meta.write_text(json.dumps({"cell": {"w": w, "h": h}, "frames": layout, "pivot": "bottom-centre"},
                               indent=2), encoding="utf-8")


def png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return buf.getvalue()
