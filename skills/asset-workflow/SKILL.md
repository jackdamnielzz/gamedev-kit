---
name: asset-workflow
description: The default reference-first art and audio pipeline for Niels's games - generate concept options, orthographic turnaround sheets and UI mockups with Nano Banana 2.1 or GPT Image 2.5 (Gemini API, OpenAI API or NanoGPT), let the human pick, then build the real assets in headless Blender via Python or as SVG/HTML/Pillow, compare against the references, and log everything for Steam AI disclosure. Also covers pixel art, image-to-3D, SFX, music, voice, licences and post-processing.
when_to_use: Whenever a game needs any visual or audio asset (units, characters, buildings, props, tiles, backgrounds, UI, icons, key art, sprites, animations, SFX, music, voice), or when choosing an AI generator, budgeting generation, or writing the Steam AI disclosure.
---

# Asset workflow

The full workflow lives in `${CLAUDE_PLUGIN_ROOT}/docs/AI-ASSET-WORKFLOW.md`. Read the relevant sections with the Read tool before generating or building anything. The most important section is "The default pipeline: AI references → Blender".

## The push rule

For every game and every new asset group, proactively propose and run the reference-first pipeline. Do not start modelling, drawing or writing final UI from a text description alone. Exceptions: greybox placeholders before the vertical slice, and assets the human explicitly says to build without references. If no image API key is set (`GEMINI_API_KEY`, `OPENAI_API_KEY` or `NANOGPT_API_KEY`), say so and ask the human to set one; do not silently skip the step.

To run the pipeline step by step, use the `new-asset` skill (`/gamedev-kit:new-asset <group>`).

## Never assume a style

The game's genre or a stack recipe does not decide its look. Exploration always shows clearly different style options, and the human picks.

## Section map

- Summary (asset type → default tool → route)
- Guiding principles (what Claude does itself, what it cannot do, push rule, rules for every pipeline)
- The default pipeline: AI references → Blender (steps 0–8, prompt template, routes A/B/C, compare loop, the three API routes, when to deviate)
- Image and 2D art (model table, style consistency, local models)
- Pixel art, sprites and animation
- 3D generation
- Sound effects · Music and adaptive music · Voice and dialogue
- NanoGPT · Aggregators, MCP servers and CLIs (for API details load the `nanogpt-api` skill)
- Post-processing and verification · The asset manifest
- Legal, licensing and Steam AI disclosure · Licence traps
- Decision checklist for a new game

## Tools in the project

A project scaffolded with `/gamedev-kit:new-game` has: `tools/gen_image.py` (provider switch, dry-run by default), `art/py/contact_sheet.py`, `art/py/slice_refs.py`, `art/py/extract_palette.py`, `art/py/compare.py`, `art/py/video_to_sprites.py` (AI animation video → grid-true frames with one shared crop, grid and palette), `art/blender/lib/refs.py`, `art/blender/sprite_unit.py`. If a project lacks them, copy them from `${CLAUDE_PLUGIN_ROOT}/templates/project/`.

Never print or commit API keys. Ask before any generation run estimated above the budget in `docs/specs/000-stack.md`.
