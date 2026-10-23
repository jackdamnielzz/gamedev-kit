# tools/pixellab — PIXEL ART ONLY

These scripts are for **pixel-art games that use PixelLab** (`docs/specs/000-stack.md` names PixelLab as the art route). In any other game, delete this folder; the general image route is `tools/gen_image.py`.

The API reference is `PIXELLAB-API.md` in the gamedev-kit (skill `gamedev-kit:pixellab-api`).

| File | Does |
| --- | --- |
| `client.py` | Shared client: key from `PIXELLAB_API_KEY` (never printed), retries with `Retry-After`, polling, downloads, balance, the generation log, manifest entries, previews and spritesheets, palette snap, pixel-art lint, review page, Phaser atlas export |
| `create_character_v3.py` | Approved south-facing sprite → PixelLab character with 4 or 8 directions (v3) |

`create_character_v3.py` in short:

- **Dry run by default**: checks the sprite (at most 256×256, transparency, binary alpha, room above and below) and prints the request and the estimated generations. `--run` generates.
- **Budget guard**: refuses above `--max-generations` (default 5) and when the balance is too low; the real cost is measured from the balance before and after.
- **Never pays twice**: the character id is written to `build/gen/characters/<name>/state.json` the moment PixelLab returns it. A second `--run` for the same name is refused (use `--force` to pay for a new one); `--resume` downloads after an interruption, `--character-id` downloads any existing character. Both are free.
- **Polls the character itself** (`GET /characters/{id}` until `completed`), not the background job.
- Downloads send a browser User-Agent: PixelLab's file host answers 403 to Python's default one.
- **Post-processing** after every download, or on its own with `--rebuild` (offline, free):
  1. **Palette snap**: all directions onto ONE palette, binary alpha, orphan pixels removed → `final/<direction>.png`. Uses `art/palette.json` when it has 8+ colours; otherwise (or with `--palette auto`) one shared palette of `--colours` (default 32) built from all directions together. The raw PixelLab files are kept.
  2. **Lint** per direction: palette colours only, no semi-transparent pixels, no orphan pixels, not an upscaled image.
  3. `sheet.png` + `sheet.json` (one row, equal cells, never rescaled, bottom-centre pivot), a labelled 4× preview and a turnaround GIF in `build/previews/`.
  4. **Review page** `build/previews/<name>_review.html` (self-contained): raw vs final, 1× and 4×, light and dark background, the turnaround GIF, warnings and lint results, for the human to approve.
  5. **Phaser export** `export/<name>.png` + `export/<name>.json` (TexturePacker JSON Hash, frames `<name>/<direction>`, pivot bottom-centre): `this.load.atlas('<name>', '<name>.png', '<name>.json')`.
  6. `report.json`, a line in `build/gen/log.jsonl`, and manifest entries (`ai_pixels_shipped: true`, `approved: false`, PixelLab licence) when `assets/manifest.json` exists.

The human still approves every character on the review page, and hero frames still get a manual Sprite Grid pass.
