---
name: new-asset
description: Run the reference-first art pipeline for one asset group in the current game - art direction check, AI exploration options (Nano Banana 2.1 / GPT Image 2.5), human pick, turnaround and UI mockup reference sheets, slicing and palette, Blender or SVG/HTML build, reference-vs-render comparison, output and manifest entry.
when_to_use: A game needs a new group of visual assets (units, characters, buildings, props, environment, UI screens, icons), or the human runs /gamedev-kit:new-asset.
argument-hint: "<asset group, e.g. units, robots, gym-interior, hud>"
---

# New asset group: $ARGUMENTS

Recommended models: Opus for art direction and judging comparisons; Sonnet is fine for writing Blender recipes once references are approved. Tell the human.

First read "The default pipeline: AI references → Blender" in `${CLAUDE_PLUGIN_ROOT}/docs/AI-ASSET-WORKFLOW.md` and the project's `docs/specs/000-stack.md` and `docs/specs/art-direction.md`.

Keep a task list with one item per step below. Stop and wait for the human at every step marked **(human)**.

## Step 0 — Art direction

If `art-direction.md` has no style paragraph yet (first asset group of the game), draft the non-style parts with the human (camera, base resolution or polygon budget, mood, 3–5 keywords). The style paragraph itself is written after step 2 from the chosen option.

## Step 1 — Explore

- Write 4–8 recipes `art/recipes/explore_<group>_<a..h>.json`, each a clearly different visual style. Never pick styles from the genre alone; vary rendering (pixel, painted, cel-shaded, flat vector, low-poly, etc.) unless the human already fixed the style in an earlier group.
- Show the estimated total cost (`python tools/gen_image.py <recipe> --estimate`) and ask before spending above the budget.
- Generate with `python tools/gen_image.py <recipe> --run` (one image per recipe).
- Build a labelled contact sheet: `python art/py/contact_sheet.py build/gen/explore_<group>_* --out build/previews/explore_<group>.png`. Read it yourself.

## Step 2 — Pick **(human)**

Show the sheet path and a one-line description per option. Wait for the pick (or a mix). Then write the fixed style paragraph into `art-direction.md` between the `<!-- style:start -->` and `<!-- style:end -->` markers and copy the chosen image to `art/refs/<group>/_style.png`.

## Step 3 — Reference sheets

For each asset in the group, write a `reference` recipe with the chosen image attached and the turnaround prompt template from the workflow doc (orthographic front / side / back / top, same scale, one ground line, flat light, plain flat background, no text). For UI groups write `ui-mockup` recipes (full screens at the target resolution plus a separate element sheet). Generate one image per recipe and make a contact sheet.

## Step 4 — Approve and extract **(human)**

After approval: move approved sheets to `art/refs/<group>/<asset>_turnaround.png`, run `npm run refs:prepare` (or `python art/py/slice_refs.py` and `python art/py/extract_palette.py` directly), check the sliced views and the palette swatch PNG, and name the palette colours with the human. Add every approved reference to `assets/manifest.json` (`kind: "reference"`).

## Step 5 — Build

Pick the route per asset and say which:

- Route A (mechanical, architectural): Blender recipe in `art/blender/<asset>.py` using `lib/refs.py` to load the views; primitives + modifiers; moving parts as separate objects with correct pivots; palette materials.
- Route B (organic): image-to-3D from the approved front view (Tripo or Meshy), then a Blender clean-up recipe.
- Route C (UI, icons): HTML+CSS / SVG / Pillow 9-slices, measured from the mockup; text from `data/i18n/`.

## Step 6 — Compare and iterate

Render the reference angles, run `python art/py/compare.py --ref <view.png> --render <render.png> --out build/previews/<asset>_compare.png`, read the image and the IoU, list differences, fix, repeat. Stop after 3–5 rounds without convergence and show the human the best result.

## Step 7 — Output **(human for hero assets)**

Render final outputs (directions, frames, GLB, atlas, UI code) as the stack recipe requires, take an in-game screenshot when the game can show it, and get approval for hero assets. Add a manifest entry per shipped file with `built_from` (reference paths), `ai_pixels_shipped` (true/false) and licence.

## Step 8 — Log

Add a short entry to `docs/MADE-WITH-AI.md` if anything in the pipeline broke or needed a workaround.
