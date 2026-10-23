---
name: asset-forge
description: Asset Forge, Niels's own AI-driven 3D and pixel-art asset workshop (github.com/jackdamnielzz/asset-forge) - 107 commands over MCP/HTTP/CLI for modelling, materials, generators (props, level kits, characters), animation, 3D-to-pixel-art sprite sheets with palettes and outlines, icons, tilesets, effects, house styles, Godot 4 export, and optional AI services including full PixelLab access. Use when a game builds 3D assets, 3D-rendered sprites, consistent props or effects, or targets Godot.
when_to_use: Building props, level pieces, 3D models or 3D-rendered sprites; choosing between Blender, Asset Forge, PixelLab or an image model for an asset group; exporting assets to Godot; or when the human mentions Asset Forge.
---

# Asset Forge

Read `${CLAUDE_PLUGIN_ROOT}/docs/ASSET-FORGE.md` first (what it is, how to connect, where it fits in the kit pipeline, when not to use it). For the commands themselves, read the tool's own `llms.txt` (live at `http://127.0.0.1:7777/llms.txt`, or in the repository) and `docs/API.md`.

Rules:

- Connect with `claude mcp add asset-forge -- node <asset-forge folder>/src/mcp/index.js`; the engine starts if needed.
- `get_scene` first; `render_preview` before calling anything done; `save_checkpoint` before experiments.
- Commands that use outside AI services (`generate_image`, `generate_video`, `generate_3d`, `pixellab_run`) cost money: show the estimate and ask the human first.
- Keep every asset's source as text in the game repo (`art/forge/<asset>.json`: a recipe or a `run_batch` list) and log exports in `assets/manifest.json`.
- Apply the project's house style (palette from `art/palette.json`) before rendering sprites, so every asset shares one palette.
- The reference-first rule still applies: the human approves designs and hero assets.
