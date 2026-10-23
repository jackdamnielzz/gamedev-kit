# tools/pixellab — PIXEL ART ONLY

These scripts are for **pixel-art games that use PixelLab** (`docs/specs/000-stack.md` names PixelLab as the art route). In any other game, delete this folder; the general image route is `tools/gen_image.py`.

The API reference is `PIXELLAB-API.md` in the gamedev-kit (skill `gamedev-kit:pixellab-api`).

| File | Does |
| --- | --- |
| `client.py` | Shared client: key from `PIXELLAB_API_KEY` (never printed), retries with `Retry-After`, polling, downloads, balance, the generation log, manifest entries, previews and spritesheets |
| `create_character_v3.py` | Approved south-facing sprite → PixelLab character with 4 or 8 directions (v3) |

`create_character_v3.py` in short:

- **Dry run by default**: checks the sprite (at most 256×256, transparency, binary alpha, room above and below) and prints the request and the estimated generations. `--run` generates.
- **Budget guard**: refuses above `--max-generations` (default 5) and when the balance is too low; the real cost is measured from the balance before and after.
- **Never pays twice**: the character id is written to `build/gen/characters/<name>/state.json` the moment PixelLab returns it. A second `--run` for the same name is refused (use `--force` to pay for a new one); `--resume` downloads after an interruption, `--character-id` downloads any existing character. Both are free.
- **Polls the character itself** (`GET /characters/{id}` until `completed`), not the background job.
- **Output**: one PNG per direction, `sheet.png` + `sheet.json` (one row, equal cells, never rescaled, bottom-centre pivot), `character.json`, `report.json` (canvas, figure height and colours per direction, warnings such as height drift between directions), a labelled 4× preview in `build/previews/`, a line in `build/gen/log.jsonl`, and manifest entries (`ai_pixels_shipped: true`, PixelLab licence) when `assets/manifest.json` exists.
- Downloads send a browser User-Agent: PixelLab's file host answers 403 to Python's default one.

After this step, the kit's cleanup still applies: snap all directions to the project palette together, lint, a manual Sprite Grid pass on hero frames, and human approval.
