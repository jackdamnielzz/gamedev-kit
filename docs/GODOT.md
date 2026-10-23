# Godot 4 recipe — an agent-built Godot game

> **Master copy:** the GitHub repo `jackdamnielzz/gamedev-kit`, folder `docs/`. Copies elsewhere follow the repo; change the repo first.

23 October 2026 · Niels. The kit's default stack is a TypeScript browser game (`GAME-STACK.md`). This page is the alternative for games where **Godot 4** is the better engine, built entirely by Claude Code: the human never has to open the Godot editor. The kit's principles stay the same (specs first, deterministic sim, content as data, guard rails, reference-first art, the asset manifest); only the tools change.

## 1. When to choose Godot

| Choose Godot when | Stay on the web stack when |
| --- | --- |
| Steam / desktop is the main target, and a small native build matters | The browser is the main target (instant play, portals, small download) |
| The look needs 2D lights with normal maps, particles, shaders, glow | Simple flat art, menus, cards |
| Assets come from Asset Forge (direct Godot export) or 3D | A heavy DOM/HTML UI |
| Console ports may follow (through porting partners) | The game must run on very old devices or in a page |

Record the choice and the reason in `docs/specs/000-stack.md`.

## 2. Tools

| Tool | Notes |
| --- | --- |
| Godot 4 (pin the exact version, e.g. 4.6.2) | Use the **console** executable for scripted runs (`Godot_v4.x-stable_win64_console.exe`); record its path in `000-stack.md` |
| Export templates (same version) | Needed for release builds; install once per version |
| Godot MCP server (optional) | Lets the agent launch the project, run it and read debug output |
| Asset Forge (`ASSET-FORGE.md`) | Exports GLB with collision, SpriteFrames, TileSets and normal maps straight into the project |
| PixelLab (`PIXELLAB-API.md`) | Characters and animations; the `tools/pixellab/` scripts write PNGs that Godot imports |

## 3. How the agent works without the editor

Everything in a Godot project is text: `project.godot`, scenes (`.tscn`), scripts (`.gd`), resources (`.tres`). The agent writes and edits them directly.

| Need | Command or method |
| --- | --- |
| Import new or changed assets | `godot --headless --path <project> --import` (run after copying files in; creates `.import` files and the `.godot/` cache) |
| Run tests / bots without a window | `godot --headless --path <project> --script res://tests/run_tests.gd` (or a test framework's runner) |
| See the game | Run without `--headless`; a debug script waits a few frames, saves `get_viewport().get_texture().get_image()` with `save_png(ProjectSettings.globalize_path(...))`, then `get_tree().quit()`. Headless mode has no renderer, so screenshots need a normal run |
| Short video for review | `--write-movie <file.avi or frames.png> --fixed-fps 30 --quit-after <frames>` on a normal run |
| Build | `godot --headless --path <project> --export-release "<preset>" <output>` with `export_presets.cfg` in the repo |

Rules for agents:

- Prefer building nodes in **scripts** or small, simple `.tscn` files; keep generated scenes readable. Never hand-edit `.import` files or anything in `.godot/` (git-ignore `.godot/`).
- After adding assets, always run the headless import before running the game.
- Read every screenshot before calling visual work done (kit rule).
- Keep `uid://` references consistent: when a resource is moved, re-import and let Godot update them; do not invent uids.

## 4. Project settings for pixel art (verified 23 October 2026, Godot 4.6.2)

```ini
[display]
window/size/viewport_width=640
window/size/viewport_height=360
window/size/window_width_override=1280
window/size/window_height_override=720
window/stretch/mode="viewport"
window/stretch/scale_mode="integer"

[rendering]
renderer/rendering_method="gl_compatibility"
textures/canvas_textures/default_texture_filter=0
2d/snap/snap_2d_transforms_to_pixel=true
```

- `viewport` stretch mode renders at the native resolution and scales up; `integer` scaling keeps every art pixel the same size.
- Texture filter 0 = Nearest: crisp pixels everywhere.
- **2D lights with normal maps work in the Compatibility renderer** (tested: `CanvasTexture` with `diffuse_texture` + `normal_texture`, a `PointLight2D` with a radial `GradientTexture2D`, a dark `CanvasModulate`). Compatibility also gives the widest hardware and web support.
- Sprites without a normal map are lit flat. Give hero sprites a normal map (Asset Forge `render_sprites maps:["normal"]`, or PixelLab `/normal-map`).

## 5. Architecture (same principles as the web stack)

```
project/
  project.godot  export_presets.cfg
  sim/            pure GDScript classes (RefCounted), no Node or scene access: rules, economy, story
  game/           autoloads and scene flow: input -> commands -> sim; sim events -> presentation
  scenes/         one scene per screen or location; presentation only
  ui/             Control-based UI, themes, the pixel font (.ttf)
  data/           JSON content + schema checks (or typed .tres resources)
  assets/         imported art and audio (Asset Forge and PixelLab output, approved only)
  tests/          unit tests, determinism test, bots
  tools/          Python and PixelLab scripts (outside the Godot import)
```

- **Deterministic sim:** a `RandomNumberGenerator` with a fixed `seed` stored in the world state; no `randi()`/`randf()` globals, no `Time` in the sim; fixed steps or turns. Same seed + same command log = same result, checked by a determinism test.
- **Content as data:** JSON in `data/` validated at load (a small schema checker script) or typed Resources; balance changes are data edits.
- **Saves:** versioned JSON in `user://`, with migrations and fixture saves, as in `GAME-STACK.md`.
- **Tests:** a test framework for GDScript (for example GUT or gdUnit4; pick one, pin its version) run headless in CI; bots play through the same command API as the player.
- **Typed GDScript** (`var x: int`, typed arrays, `class_name`) as the agent guard rail, with warnings treated as errors in project settings.

## 6. Assets into Godot

| Source | How it arrives |
| --- | --- |
| Asset Forge 3D | `export_godot` / `export_each`: GLB with collision and AnimationPlayer in `assets/forge/` |
| Asset Forge sprites | `render_sprites` with `project`: PNG + SpriteFrames `.tres` (+ normal map); `make_tileset` writes a TileSet with terrains |
| PixelLab characters | `tools/pixellab/create_character_v3.py` → `final/*.png` + sheet JSON; a small import script builds `SpriteFrames` per animation |
| Lighting | `CanvasTexture` (diffuse + normal) on `Sprite2D` / `AnimatedSprite2D`; `PointLight2D` for lamps, spotlights and neon; `CanvasModulate` for the room's base mood; `LightOccluder2D` for shadows where needed |
| Effects | Asset Forge `make_effect` sprite strips, `GPUParticles2D`/`CPUParticles2D` for dust, sweat and confetti |

Only approved assets go into `assets/`; every file has a manifest entry.

## 7. CI and release

- GitHub Actions: download the pinned Godot (and export templates) in the workflow, cache them, run the headless import, the tests and the bots, then export.
- Desktop: export presets for Windows, Linux (Steam Deck) and macOS. Steam features through a Steamworks extension for Godot (for example GodotSteam); verify its version against the pinned Godot.
- Web demo: the Web export works but is heavier than the TypeScript stack; test load time.

## 8. Known pitfalls

| Pitfall | Rule |
| --- | --- |
| Blurry or uneven pixels | Nearest filter, `viewport` stretch, integer scale, snap 2D transforms; never scale sprites by non-integer factors |
| Assets missing at runtime after copying files | Run the headless import first |
| Screenshot is black or missing | Headless mode cannot render; capture from a normal run after a few frames |
| Flat-looking lit sprites | Add normal maps to the sprites the light touches |
| Sim logic inside nodes | Keep rules in `sim/` classes; scenes only read state and send commands |
| Hidden randomness | One seeded `RandomNumberGenerator` in the world state; determinism test in CI |
