# Asset Forge — our own AI-driven asset workshop

> **Master copy:** the GitHub repo `jackdamnielzz/gamedev-kit`, folder `docs/`. Copies elsewhere follow the repo; change the repo first.

23 October 2026 · Niels. Asset Forge (https://github.com/jackdamnielzz/asset-forge, version 0.1.0) is Niels's own tool: a small Blender-like 3D and pixel-art asset workshop in which **every action is a command an AI can call**. This page tells a game project when to use it, how to connect it, and where it fits in the kit's pipeline. The tool's own documentation is complete and generated from the code: `llms.txt`, `docs/API.md` (every command and setting) and `docs/openapi.json` in its repository, or live at `http://127.0.0.1:7777/llms.txt` and `/docs` while it runs.

## 1. What it is

| | |
| --- | --- |
| What | A local 3D + pixel-art asset tool (three.js, Node, no build step) with a window you can watch live while an AI builds |
| Control | 107 commands through MCP, HTTP (`POST /api/commands/<name>`), OpenAPI 3.1 and a CLI; the window calls the same commands |
| "Eyes" for the AI | `render_preview` returns a picture, so the agent can look, judge and fix (the kit's rule 8: read your own previews) |
| Output | `.glb` (with animations), PNG, sprite sheets, `.aseprite`, Godot 4 files (scenes with collision, SpriteFrames, TileSets) |
| Not | A game engine. It makes the pieces; the engine puts them together |
| Licence | **No licence in the repository yet**: free to try, but nobody may legally copy or reuse its code. Our own games may use its output |
| Cost | Free and local; only the optional outside AI services cost money (your own keys) |

Requirements: Node 20+, and Chrome or Edge (used invisibly to render). Start with `npm install` then `npm start` (window at `http://127.0.0.1:7777`), or on Windows `Install Asset Forge.bat` for a desktop icon.

## 2. Connecting it to Claude Code

| Where | How |
| --- | --- |
| Any game folder | `claude mcp add asset-forge -- node D:/Programmeren/asset-forge/src/mcp/index.js` (starts the engine if needed) |
| Scripts / CI on the same computer | `POST http://127.0.0.1:7777/api/commands/<name>` with a JSON body; answers `{ "ok": true, "result": … }`; pictures as base64 or `?format=png` |
| Terminal | `node D:/Programmeren/asset-forge/src/cli/forge.js <command> key=value …` or `… @args.json` |
| Another computer | `Share Asset Forge.bat` sets a password; callers send `Authorization: Bearer <password>` and cannot use file paths |

Golden rules from the tool itself: call `get_scene` first; look with `render_preview` before saying something is done; `save_checkpoint` before experiments; **ask the human before** `generate_image`, `generate_video`, `generate_3d` and `pixellab_run` (they cost money).

## 3. What it can do (command groups)

| Group | Commands (selection) | Use in a game pipeline |
| --- | --- | --- |
| Modelling | `add_object` (box, sphere, cylinder, cone, torus, capsule, lathe, extrude, text, rock, cutout, voxels, model), `cut_object`, `mirror_object`, `repeat_object`, `group_objects` | Build props and set pieces from primitives, like the kit's Blender Route A, but every step is a command |
| Looks | `set_material` (26 presets incl. generated oak, planks, worn/rusty metal, cobblestone, brick, cloth, concrete, hand-painted; `wear` 0–1), `set_environment` (6 lighting moods), `set_style` (realistic, toon, low-poly, clay), `set_effects` (soft shadows, glow) | Good-looking 3D without textures to draw |
| Generators | `make_crate`, `make_barrel`, `make_chest`, `make_rock`, `make_tree`, `make_crystal`, `make_potion`, `make_sword`, `make_coin`, `make_lamp_post`, `make_fence`, `make_level_kit` (dungeon, cottage, sci-fi), `make_character` (chibi or normal, idle/walk/run/attack/jump) | Whole props from one command with a seed; `make_variations` for options, `remake` for changes |
| Animation | `animate_object` (spin, bob, pulse, swing, hinge, shake, hop), `set_keyframes` | Baked into GLB and sprite sheets |
| Sprites from 3D | **`render_sprites`** (1/4/8 directions × frames, `elevation` 0 = side … 30 = 2:1 iso … 60+ = top-down, fixed `pixelsPerMetre`, palette, dither, outline incl. `selout`, clean-up, normal and emission maps, Godot SpriteFrames), `make_prop_sheet`, `make_icons`, `make_iso_tiles` | The kit's "3D → rendered sprites" animation route, with consistent scale and camera for every asset |
| 2D pixel tools | `make_tileset` (16 corner autotiles + Godot TileSet), `make_effect` (explosion, fire, smoke, magic, sparks, glitter, heal, lightning), `make_parallax`, `pixelate_image`, `recolor_image`, `make_palette_variants`, `extract_palette`, `check_pixel_style`, `paint_pixels`, `video_to_sprites`, `export_aseprite`, voxels and `.vox` import | Free effects, palettes and checks without AI generations |
| Consistency | **House styles** (`save_house_style`, `apply_house_style`: one palette + lighting + style for a whole game; sprites, tiles and effects then use its palette), recipes (`save_recipe`, `use_recipe`), `check_quality` (floating parts, odd sizes, polygon count, beauty tips) | One look across all assets |
| Godot | `export_godot`, `export_each` (GLB with collision and AnimationPlayer straight into a Godot 4 project), SpriteFrames and TileSet `.tres` from the 2D commands; tested in Godot 4.6 | Direct hand-off when a game uses Godot |
| Outside AI (optional, own keys) | `generate_image` (OpenAI, Gemini, NanoGPT, PixelLab; `referenceRender` sends a render of a 3D object as the reference), `generate_video` (NanoGPT), `generate_3d` (fal: Trellis 2, Hunyuan 3D), **`pixellab_tools` / `pixellab_tool_info` / `pixellab_run`** (every PixelLab endpoint, read live from its OpenAPI spec), `pixellab_balance` | "Our render as guide, AI paints the pixels"; the kit's cost rules still apply |
| Safety | Autosave, versions and checkpoints, daily backups (7 kept), asset library with thumbnails and search | — |

## 4. Where it fits in the kit pipeline

The kit's reference-first rule still holds: designs come from approved references, the human picks, and every asset is logged in `assets/manifest.json`.

| Kit step | Without Asset Forge | With Asset Forge |
| --- | --- | --- |
| Route A: mechanical/architectural assets from primitives | Headless Blender recipe (`bpy`) | Asset Forge commands (a recipe JSON or a `run_batch`), watched live, checked with `render_preview` and `check_quality`; export GLB or sprites |
| Animation route 1: 3D → rendered sprites | Blender render script + cleanup | `render_sprites` with a fixed `pixelsPerMetre`, `elevation` and the project palette (house style) |
| Props for 2D scenes | Image model or PixelLab per prop | Model once, render with the same camera and scale as every other prop (`make_prop_sheet`); free per render |
| Pixel effects, parallax, simple tilesets | PixelLab / code | `make_effect`, `make_parallax`, `make_tileset` (free) |
| Repainting a 3D blockout as pixel art | — | `pixellab_run` or `generate_image` with `{ render: <object id> }` / `referenceRender` (costs generations) |
| Godot projects | Manual import | `export_godot`, SpriteFrames, TileSet, normal maps for 2D lights |

**When to choose it:**

- Assets that must match each other exactly in scale and camera angle (props in rooms, isometric pieces, items, icons).
- 3D games or 3D-rendered sprites, especially in Godot.
- Free, repeatable work (effects, icons, prop variations) instead of paid generations.

**When not:**

- Hand-drawn-looking characters. The built-in `make_character` is a simple jointed chibi or normal figure that reads as "3D-rendered"; for detailed pixel-art characters use PixelLab (or repaint an Asset Forge render with PixelLab).
- Organic hero models: use image-to-3D (fal through `generate_3d`, Tripo, Meshy) and refine in Asset Forge.

## 5. Recording it in a project

- In `docs/specs/000-stack.md`, name Asset Forge as the build tool for the asset groups that use it, with the Asset Forge commit or version.
- Save the project's **house style** in Asset Forge from the approved palette (`save_house_style` with the hex colours of `art/palette.json`) and apply it before every render.
- Keep the source of each asset as text in the game repo: a saved recipe or a `run_batch` command list in `art/forge/<asset>.json`, so the asset can be rebuilt. Exports go to `workspace/exports/` (or straight into a Godot project); copy the approved ones into the game.
- Manifest entries: `provider: "asset-forge"`, the recipe path, `ai_pixels_shipped: false` for pure renders (code-built), `true` when an AI service painted pixels.

## 6. Quality notes from a first review (23 October 2026)

- The 3D generators (crate, barrel, chest, rocks, trees, fence, lamp post, level kits) look polished in their stylised default look, with generated wood, stone and metal and soft shadows.
- Built-in pixel-art characters and the default iso tiles and parallax are simple: fine for prototypes, not at the level of hand-drawn or PixelLab sprites.
- The test suite (`npm test`, `npm run test:godot`) checks every command and real Godot 4 import; outside AI calls are only tested against a mock.
- Keys live in `workspace/secrets.json`, which git ignores; commands never return keys.

## 7. Field test (23 October 2026): a bar counter next to a PixelLab character

- Built a bar counter with two stools from primitives (oak and dark-wood presets, brass rail, chrome taps) in one `run_batch`; `check_quality` scored 100.
- `render_sprites` with `directions: 1`, `elevation: 20` and `pixelsPerMetre: 34` matched the scale and camera of a 64 px PixelLab character drawn in "low top-down" view; with the character's palette the two read as one family. Cost: 0 generations.
- Lessons: give the project palette **neutral greys** (chrome otherwise snaps to cream); `outlineStyle: "solid"` with the darkest palette colour matches PixelLab's dark outlines better than `selout`; brighter lighting presets wash out wood, so pick darker material colours or the `dramatic` preset.
- In Godot 4.6 (Compatibility renderer) the normal map made a single `PointLight2D` light the counter top warmly while the front stayed dark: real depth at pixel scale.
- A single PixelLab prop looks more hand-drawn; Asset Forge wins on consistency across many props, normal maps and free changes. Repainting an Asset Forge render with PixelLab (`edit-image-pixen` or `pixellab_run` with `{ render: <id> }`) combines both.
