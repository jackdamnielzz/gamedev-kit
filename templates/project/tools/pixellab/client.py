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
import math
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


# ----------------------------------------------------------------------------- palette (proposal 1)
def load_palette(path: Path) -> list[tuple[int, int, int]]:
    """Read art/palette.json: a {"_hex": {...}} block, linear-RGB 0-1 entries, or a list of hex strings."""
    data = json.loads(path.read_text(encoding="utf-8"))
    hexes: list[str] = []
    if isinstance(data, list):
        hexes = data
    elif isinstance(data.get("_hex"), dict):
        hexes = list(data["_hex"].values())
    else:
        out = []
        for k, v in data.items():
            if k.startswith("_") or not isinstance(v, list) or len(v) < 3:
                continue
            srgb = [(c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055) for c in v[:3]]
            out.append(tuple(max(0, min(255, round(c * 255))) for c in srgb))
        return out
    return [tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)) for h in hexes]


def shared_palette(frames: list[Image.Image], colours: int) -> list[tuple[int, int, int]]:
    """One palette for ALL frames together (median cut over every opaque pixel), so directions never drift."""
    import numpy as np
    px = np.concatenate([np.asarray(f.convert("RGBA")).reshape(-1, 4) for f in frames])
    px = px[px[:, 3] >= 128][:, :3]
    if len(px) == 0:
        return []
    strip = Image.fromarray(px.reshape(1, -1, 3).astype("uint8"), "RGB")
    q = strip.quantize(colors=min(colours, 256), method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = q.getpalette()[: 3 * len(q.getcolors(256) or [])]
    return [tuple(pal[i:i + 3]) for i in range(0, len(pal), 3)]


def snap(img: Image.Image, palette: list[tuple[int, int, int]]) -> Image.Image:
    """Every opaque pixel -> nearest palette colour (perceptual 'redmean' distance); alpha -> 0 or 255;
    single opaque pixels with no opaque 4-neighbour (orphans) are dropped."""
    import numpy as np
    a = np.asarray(img.convert("RGBA")).astype(np.int32)
    pal = np.asarray(palette, dtype=np.int32)
    rgb = a[..., :3].reshape(-1, 1, 3)
    rmean = (rgb[..., 0] + pal[None, :, 0]) / 2
    d = rgb - pal[None, :, :]
    dist = (2 + rmean / 256) * d[..., 0] ** 2 + 4 * d[..., 1] ** 2 + (2 + (255 - rmean) / 256) * d[..., 2] ** 2
    idx = dist.argmin(axis=1).reshape(a.shape[:2])
    out = np.zeros_like(a)
    out[..., :3] = pal[idx]
    opaque = a[..., 3] >= 128
    pad = np.pad(opaque, 1)
    neighbours = pad[:-2, 1:-1].astype(int) + pad[2:, 1:-1] + pad[1:-1, :-2] + pad[1:-1, 2:]
    opaque &= neighbours > 0
    out[..., 3] = np.where(opaque, 255, 0)
    out[out[..., 3] == 0] = 0
    return Image.fromarray(out.astype("uint8"), "RGBA")


# ----------------------------------------------------------------------------- lint (proposal 2)
def lint(img: Image.Image, palette: list[tuple[int, int, int]] | None) -> dict:
    """Real-pixel-art checks: palette only, binary alpha, no orphan pixels, not an upscaled image."""
    import numpy as np
    a = np.asarray(img.convert("RGBA")).astype(np.int32)
    opaque = a[..., 3] > 0
    issues = []
    semi = int(((a[..., 3] > 0) & (a[..., 3] < 255)).sum())
    if semi:
        issues.append(f"{semi} semi-transparent pixels")
    colours = {tuple(c) for c in a[opaque][:, :3].tolist()}
    off = len(colours - set(palette)) if palette else 0
    if off:
        issues.append(f"{off} colours not in the palette")
    pad = np.pad(opaque, 1)
    neighbours = pad[:-2, 1:-1].astype(int) + pad[2:, 1:-1] + pad[1:-1, :-2] + pad[1:-1, 2:]
    orphans = int((opaque & (neighbours == 0)).sum())
    if orphans:
        issues.append(f"{orphans} orphan pixels (opaque, no opaque neighbour)")
    h, w = opaque.shape
    if h >= 4 and w >= 4 and h % 2 == 0 and w % 2 == 0:
        blocks = a[0::2, 0::2]
        if all((a[dy::2, dx::2] == blocks).all() for dy in (0, 1) for dx in (0, 1)):
            issues.append("looks upscaled 2x (every 2x2 block is one colour): use the native size")
    return {"pass": not issues, "issues": issues, "colours": len(colours), "orphans": orphans,
            "semi_transparent": semi, "off_palette": off}


# ----------------------------------------------------------------------------- review page (proposal 7)
def turn_gif(frames: list[tuple[str, Image.Image]], out: Path, scale: int = 4, ms: int = 250) -> None:
    w = max(f.width for _, f in frames) * scale
    h = max(f.height for _, f in frames) * scale
    imgs = []
    for _, f in frames:
        bg = Image.new("RGBA", (w, h), (128, 128, 128, 255))
        big = f.resize((f.width * scale, f.height * scale), Image.NEAREST)
        bg.alpha_composite(big, ((w - big.width) // 2, h - big.height))
        imgs.append(bg.convert("P", palette=Image.ADAPTIVE))
    imgs[0].save(out, save_all=True, append_images=imgs[1:], duration=ms, loop=0, disposal=2)


def review_page(name: str, raw: list[tuple[str, Image.Image]], final: list[tuple[str, Image.Image]],
                report_data: dict, gif: Path, out: Path) -> None:
    """Self-contained HTML (images embedded) for the human to judge a character before approval."""
    import html as _html
    b64 = lambda img: base64.b64encode(png_bytes(img)).decode()  # noqa: E731
    gif64 = base64.b64encode(gif.read_bytes()).decode()
    warnings = report_data.get("warnings", []) + [f"{d}: {', '.join(l['issues'])}" for d, l in
                                                  report_data.get("lint", {}).items() if not l["pass"]]
    rows = []
    for (d, r), (_, f) in zip(raw, final):
        lint_d = report_data.get("lint", {}).get(d, {})
        stats = report_data.get("directions", {}).get(d, {})
        rows.append(f"""<tr><th>{_html.escape(d)}</th>
<td class="light"><img src="data:image/png;base64,{b64(f)}" class="x1"></td>
<td class="light"><img src="data:image/png;base64,{b64(r)}" class="x4"></td>
<td class="light"><img src="data:image/png;base64,{b64(f)}" class="x4"></td>
<td class="dark"><img src="data:image/png;base64,{b64(f)}" class="x4"></td>
<td>{stats.get('height', '')} px<br>{lint_d.get('colours', '')} colours<br>{'✔ lint' if lint_d.get('pass') else '✖ ' + _html.escape('; '.join(lint_d.get('issues', [])))}</td></tr>""")
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_html.escape(name)} review</title><style>
:root {{ color-scheme: light dark; --bg:#f4f2ee; --fg:#222; --card:#fff; --line:#ddd; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#1d1f22; --fg:#eee; --card:#2a2d31; --line:#444; }} }}
body {{ margin:0; padding:16px; background:var(--bg); color:var(--fg); font:15px/1.5 system-ui, sans-serif; }}
h1 {{ margin:0 0 4px; }} .meta {{ opacity:.75; margin-bottom:16px; }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:8px; padding:12px; margin-bottom:16px; overflow-x:auto; }}
img {{ image-rendering: pixelated; display:block; }} .x1 {{ width:auto; }} .x4 {{ width:256px; max-width:40vw; }}
table {{ border-collapse:collapse; }} th, td {{ padding:6px 10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:middle; }}
.light {{ background:#c8c8c8; }} .dark {{ background:#26282c; }} .warn {{ color:#c0392b; }}
</style></head><body>
<h1>{_html.escape(name)}</h1>
<div class="meta">PixelLab character {_html.escape(str(report_data.get('character_id')))} · generations spent: {report_data.get('generations_spent')} ·
height {report_data.get('height_range')} px · palette: {_html.escape(str(report_data.get('palette_source')))} ({report_data.get('palette_size')} colours)</div>
<div class="card"><h2>Turnaround</h2><img src="data:image/gif;base64,{gif64}" style="width:256px"></div>
<div class="card"><h2>Warnings</h2>{'<ul>' + ''.join(f'<li class="warn">{_html.escape(w)}</li>' for w in warnings) + '</ul>' if warnings else '<p>None.</p>'}</div>
<div class="card"><h2>Directions</h2><table><tr><th></th><th>1× final</th><th>4× raw</th><th>4× final</th><th>4× on dark</th><th>Checks</th></tr>
{''.join(rows)}</table></div>
<p>Approve or reject in the chat; nothing ships before approval.</p></body></html>"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")


# ----------------------------------------------------------------------------- Phaser export (proposal 8)
def phaser_atlas(name: str, frames: list[tuple[str, Image.Image]], out_dir: Path, pad: int = 1) -> dict:
    """Atlas PNG + TexturePacker 'JSON Hash' that Phaser loads with this.load.atlas(key, png, json).
    Frames are named '<name>/<direction>' (or '<name>/<anim>/<direction>/<n>' by callers), never rescaled;
    every frame keeps its full canvas so the pivot (bottom-centre) is the same for all."""
    w = max(f.width for _, f in frames)
    h = max(f.height for _, f in frames)
    cols = min(len(frames), 8)
    rows = math.ceil(len(frames) / cols)
    atlas = Image.new("RGBA", (cols * (w + pad), rows * (h + pad)), (0, 0, 0, 0))
    data = {}
    for i, (key, f) in enumerate(frames):
        x, y = (i % cols) * (w + pad), (i // cols) * (h + pad)
        atlas.alpha_composite(f, (x + (w - f.width) // 2, y + (h - f.height)))
        data[key] = {"frame": {"x": x, "y": y, "w": w, "h": h}, "rotated": False, "trimmed": False,
                     "spriteSourceSize": {"x": 0, "y": 0, "w": w, "h": h}, "sourceSize": {"w": w, "h": h},
                     "pivot": {"x": 0.5, "y": 1.0}}
    out_dir.mkdir(parents=True, exist_ok=True)
    png, js = out_dir / f"{name}.png", out_dir / f"{name}.json"
    atlas.save(png)
    js.write_text(json.dumps({"frames": data, "meta": {
        "app": "gamedev-kit tools/pixellab", "version": "1.0", "image": png.name, "format": "RGBA8888",
        "size": {"w": atlas.width, "h": atlas.height}, "scale": "1"}}, indent=2), encoding="utf-8")
    return {"png": png, "json": js, "frames": list(data)}
