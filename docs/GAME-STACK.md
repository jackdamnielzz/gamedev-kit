# Claude-Driven Game Dev Stack

> **Master copy:** the GitHub repo `jackdamnielzz/gamedev-kit`, folder `docs/`. Copies elsewhere (the claude.ai "Game Dev" project, older game repos) follow the repo; change the repo first.

## Purpose and how to use this document

This is a reference catalogue of tools, patterns and rules for building games where an AI agent (Claude Code) does almost all of the hands-on work: code, art, audio, levels, tests and deployment. Every component is chosen because it can be driven entirely from a terminal, through text files and scripts.

How the AI should use it:

- Treat it as a menu, not a mandate. For each new game, pick one option per layer from the overview table and record the choice in the project's `CLAUDE.md` and `docs/specs/000-stack.md`.
- Defaults are marked as such. Deviate only when the game type requires it, and write down why.
- **One default is pushed actively: the reference-first art pipeline** (AI image model → human picks → Claude builds in Blender or code from the references). Claude proposes it at the start of every game's art work and for every new asset group, without waiting to be asked. See "Art pipeline".
- Once a choice is recorded in a spec, do not re-argue it in later sessions unless the human asks.
- The human designs and playtests; agents build. When a choice is genuinely ambiguous, ask the human instead of guessing.

How the human should use it: install the `gamedev-kit` Claude Code plugin once at user scope (it carries this document, `AI-ASSET-WORKFLOW.md`, `NANOGPT-API.md` and the indie development guide as on-demand knowledge, plus `/gamedev-kit:new-game` to scaffold a project, `/gamedev-kit:new-asset` to run the reference-first pipeline, `/gamedev-kit:game-concept`, `/gamedev-kit:stack-advisor` and `/gamedev-kit:sync-docs`). Install steps are in the plugin's `README.md`. Without the plugin, copy this document into a new repository as `docs/GAME-STACK.md` and reference it from `CLAUDE.md`. Install Blender once on the machine (and pin the version per game); Claude drives it through Python.

Companion documents:

- `AI-ASSET-WORKFLOW.md` — the reference-first pipeline in detail, which AI generator to use for each asset type (images, pixel art, 3D, SFX, music, voice), prices, licences, post-processing and Steam AI disclosure.
- `NANOGPT-API.md` — full API reference for NanoGPT, one of the gateways for AI asset generation.
- `indie-game-development-guide.md` — lifecycle, design craft, market, marketing and release.

## Core principles

Everything in the project must be readable, writable and runnable by an agent without a GUI. These nine rules follow from that.

1. **Everything is text or a script.** Code, data, levels, art recipes and music recipes live in the repo as source. Binary outputs (PNG, glTF, OGG) are build artefacts generated from that source. For AI-generated images the recipe is the prompt, model id, references and post-processing steps.
2. **One command rebuilds everything.** `npm run assets` regenerates all code-built art and audio; `npm run build` produces the shippable game. No manual export steps. AI-generated images (references and any shipped images) are generated once, approved, committed, and listed in the manifest.
3. **Simulation is separate from presentation.** Game rules run in a pure, deterministic module with no access to the DOM, renderer, audio or wall clock. Rendering only reads simulation state.
4. **Determinism.** Fixed timestep, seeded PRNG, no `Math.random()` or `Date.now()` inside the simulation. The same seed and inputs always produce the same result.
5. **Specs first.** Every feature starts as a short written spec with decisions recorded. Agents implement specs; they do not invent design.
6. **Guard rails instead of reading every line.** Types, schemas, unit tests, end-to-end tests, bots and performance budgets catch mistakes so the human does not have to review all code.
7. **Small tasks, fresh agents.** A coordinator splits work into small tasks with clear file ownership. A fresh agent with a tight brief beats one long session.
8. **The AI must be able to see its output.** Every visual pipeline produces PNG previews (contact sheets, reference-vs-render comparisons, screenshots) that the agent reads back to judge quality before reporting done.
9. **Reference first.** Every visual asset group starts with AI-generated design options and reference sheets that the human picks from. Claude builds the real assets to match the approved references; it does not design final art from a text description alone.

## Stack overview

The default is a TypeScript browser game built with Vite. Art follows the reference-first pipeline: Nano Banana 2.1 (or GPT Image 2.5) makes concept options, turnaround sheets and UI mockups; Claude then builds the assets in headless Blender via Python, or as SVG / HTML+CSS / Pillow for 2D and UI. SFX are synthesized from code. Pick one option per row and record it in `docs/specs/000-stack.md`.

| Layer | Default | Alternatives | Pick the alternative when |
| --- | --- | --- | --- |
| Language | TypeScript (strict) | — | Always TypeScript; strict types are a guard rail for agents |
| Build / dev server | Vite | esbuild alone | Tiny prototypes only |
| 2D rendering | Phaser | PixiJS; raw Canvas 2D | PixiJS for custom engines or heavy sprite counts; Canvas 2D for very simple games |
| 3D rendering | Three.js | Babylon.js | Babylon when you want more built-in engine features (physics, GUI, inspector) |
| Entity model | Plain typed objects + systems | bitECS; miniplex | ECS when entity counts exceed a few thousand |
| Physics | Custom / none | Rapier (WASM); planck.js (2D) | Rigid-body behaviour matters to gameplay |
| Pathfinding | Custom A* / flow fields | pathfinding.js | Grid games that need quick standard A* |
| UI / HUD | DOM overlay (HTML + CSS), rebuilt from AI mockups | Engine-native UI | Pixel-perfect in-canvas UI is required |
| Data validation | zod schemas | JSON Schema + ajv | Data is also edited by non-TS tools |
| **Reference images (concepts, turnarounds, UI mockups)** | **Nano Banana 2.1 (`gemini-nano-banana-2.1`) via `tools/gen_image.py`** | GPT Image 2.5 Flare; Nano Banana Pro; any of them via Gemini direct, OpenAI direct or NanoGPT | GPT Image 2.5 when transparency is needed; Pro for complex scenes or text-heavy mockups |
| 3D / sprite art | Blender headless + Python (`bpy`), built from approved references (Route A) | Image-to-3D (Tripo, Meshy) from the approved reference, then Blender (Route B) | Organic models the primitive route cannot build |
| 2D art / UI / icons | SVG, HTML+CSS, Python + Pillow + numpy, rebuilt from approved mockups (Route C) | Shipping the AI image directly (GPT Image 2.5, transparent); Aseprite CLI | Painted elements code cannot reproduce; hand-tuned pixel art with an Aseprite licence |
| Shipped AI images | Only where code cannot reach the look (portraits, key art, painted frames) | fal.ai FLUX LoRA (bulk); PixelLab / Retro Diffusion (pixel art) | See AI-ASSET-WORKFLOW.md per asset type |
| Texture atlas | Python packer (rectpack) | free-tex-packer-core | A Node-only pipeline is preferred |
| Sound effects | ZzFX / jsfxr parameters in JSON | Python numpy synthesis; ElevenLabs Sound Effects | Complex layered SFX; realistic foley and ambience |
| Music | Suno by hand (stems) or Python/SuperCollider rendered offline | ElevenLabs Music / Lyria API; Tone.js live | Agent-generated variations; adaptive live music |
| Voice | None (text, barks) | ElevenLabs TTS direct | The game needs spoken lines |
| Audio playback | Web Audio API (thin wrapper) | Howler.js | Many formats and fallbacks are needed quickly |
| Levels / maps | LDtk (JSON) | Tiled (.tmj JSON); procedural only | Tiled when using Phaser's built-in tilemap loader |
| Saves | Versioned JSON in IndexedDB / localStorage, with migrations | — | — |
| Unit tests | Vitest | — | — |
| Property tests | fast-check | — | — |
| End-to-end tests | Playwright | — | — |
| Lint / format | ESLint + Prettier | Biome | Faster single tool preferred |
| CI | GitHub Actions | — | — |
| Web hosting | GitHub Pages | itch.io (butler CLI); Cloudflare Pages | Public release, or a custom domain |
| Desktop / Steam | Electron + steamworks.js | Tauri | Tauri when bundle size matters more than easy Steam integration |

## Game runtime

The runtime is split into a pure simulation core and a presentation layer that only reads from it. This split is what makes bots, replays, tests and saves cheap.

### Layers

- `src/sim/` — game rules. Pure TypeScript, no imports from the renderer, DOM, audio or `window`. Exposes a small API: `createWorld(seed, config)`, `step(world, inputs)`, `serialize(world)`, `deserialize(data)`.
- `src/game/` — glue. Owns the fixed-timestep loop, translates keyboard/mouse into input commands, feeds them to the sim.
- `src/render/` — draws the current sim state with Phaser, PixiJS or Three.js. Interpolates between ticks for smooth motion. Never mutates sim state.
- `src/ui/` — HUD and menus as a DOM overlay. Reads state, emits commands.
- `src/audio/` — reacts to sim events (`unitDied`, `oreMined`) and plays sounds.
- `src/data/` — typed loaders for JSON content, validated with zod at load time.

### Simulation rules

- Fixed timestep, e.g. 20 or 30 ticks per second; rendering runs at display rate and interpolates.
- All randomness through one seeded PRNG stored in the world state (e.g. mulberry32 or sfc32). Never `Math.random()`.
- No wall-clock time in the sim; time is the tick counter.
- Players and bots act only through the same command objects (`{type: "build", part: "engine", x: 3, y: 1}`). This guarantees bots test the real game.
- The sim emits events; presentation layers subscribe. The sim never calls rendering or audio.
- Avoid relying on `Math.sin`/`Math.cos` results being bit-identical across browsers if multiplayer lockstep is ever needed; use fixed-point or lookup tables in that case.

### Rendering choices

- **Phaser**: complete 2D framework (scenes, input, tilemaps, cameras, sprite animation). Best default for 2D.
- **PixiJS**: fast 2D renderer only. Choose it when the game needs a custom engine or tens of thousands of sprites.
- **Three.js**: 3D, including top-down 3D with an orthographic camera. Use `InstancedMesh` for many identical objects and `renderer.info` to monitor draw calls.
- Pixel-art games: render to a low-resolution target and scale up with nearest-neighbour filtering; disable anti-aliasing and round sprite positions to whole pixels.

### Saves

- A save is `{ version: number, data: SerializedWorld }` as JSON in IndexedDB (large) or localStorage (small).
- Every save-format change bumps `version` and adds a migration function `migrate_N_to_N+1`. Unit tests load fixture saves from every past version.

## Art pipeline

The default art pipeline for every game is **reference-first**: an AI image model designs, the human picks, Claude builds. Nano Banana 2.1 (or GPT Image 2.5) produces style options, orthographic turnaround sheets and UI mockups; the approved images go to `art/refs/`; Claude then builds the in-game assets in Blender (driven by Python, without its interface) for anything 3D or rendered, and in SVG, HTML+CSS or Pillow/numpy for flat 2D work and UI, checking its result against the references. Raw AI images ship only where code cannot reach the look (portraits, key art, painted frames). The full pipeline, prompts and provider routes are in `AI-ASSET-WORKFLOW.md`, section "The default pipeline: AI references → Blender". Nothing is hand-drawn or downloaded unless the human explicitly adds it.

### Reference-first workflow (summary)

1. **Art direction.** `docs/specs/art-direction.md`: mood, camera, size or polygon budget, 3–5 visual keywords, one fixed style paragraph used in every prompt.
2. **Explore.** 4–8 options per asset group via `python tools/gen_image.py art/recipes/explore_<group>.json`; Claude builds a labelled contact sheet and the human picks.
3. **Reference sheets.** With the pick attached: orthographic turnarounds (front, side, back, top; flat light; plain background; no perspective), detail callouts, colour swatches, in-game-view mockups, full UI screens and UI element sheets.
4. **Approve and extract.** Approved sheets to `art/refs/<group>/`; `npm run refs:prepare` slices the views and extracts `art/palette.json`.
5. **Build.** Route A: Blender recipe from primitives with the views loaded as reference image planes. Route B: Tripo / Meshy from the approved view, then a Blender clean-up recipe. Route C: UI and icons rebuilt as HTML+CSS, SVG or Pillow 9-slices.
6. **Compare.** `npm run assets:compare -- <asset>` renders at the reference angles and writes a side-by-side + silhouette overlay; Claude reads it and iterates, at most 3–5 rounds before asking the human.
7. **Output and verify.** Sprites, GLB, atlases, UI code; in-game screenshot; human approval for hero assets; manifest entry.

Greybox placeholders without references are fine during prototyping; the reference step starts no later than the vertical slice.

### Headless Blender

- Run: `blender --background --factory-startup --python art/blender/build_ship.py -- --out build/art/ship --variant scout`. Arguments after `--` reach the script via `sys.argv`.
- Pin one Blender version for the project (record it in `000-stack.md`); the `bpy` API changes between major versions.
- Each asset is one recipe script (or one entry in a shared parametric script). It loads its reference views from `art/refs/`, builds geometry from primitives and modifiers (bevel, array, mirror, boolean, solidify, subdivision) to match them, assigns palette materials, sets lights and camera, then renders or exports.
- Moving parts (turrets, wheels, arms, doors) are separate objects with pivots at their real hinge points, so they can be animated or rotated per frame.
- Shared helpers live in `art/blender/lib/`: scene reset, reference planes, palette materials, standard lighting rig, camera rigs, render settings, comparison renders.
- Render engines: Eevee for fast, stylised renders; Cycles for higher quality when time allows; Workbench for flat previews and silhouette checks.
- Export 3D models with `bpy.ops.export_scene.gltf(filepath=..., export_format='GLB')` for Three.js.
- AI-generated models (Tripo, Meshy) are imported as GLB, re-materialled with the project palette and lighting rig, compared against their reference, and rendered through the same scripts.
- An interactive Blender MCP may be used to explore a build live, but only the committed recipe script counts.

### Sprites from 3D

- Use an orthographic camera at a fixed angle (top-down, or isometric at about 30° elevation), the same angle as the in-game-view reference mockup.
- Rotate the model, not the camera: render 8 or 16 directions per unit, and N frames per animation.
- Render with a transparent background (`film_transparent = True`), then pack frames into a spritesheet plus a JSON frame map.
- Optional outline and team-colour masks: render a second pass with an emission-only material so the game can tint factions at runtime.

### Pixel-art look

- Render small (e.g. 64×64 per frame) or render large and downscale with nearest-neighbour.
- Quantize to the project palette (extracted from the approved references) with Pillow (`Image.quantize(palette=...)`) and disable dithering for crisp edges.
- Keep the palette as `art/palette.json`; every script reads it so all assets stay consistent.
- General image models are used for pixel-art design references only. Generated pixel sprites come from PixelLab or Retro Diffusion (with the reference attached) and always pass through `unfake` (grid snap + palette) before use.

### Flat 2D, UI and icons

- UI screens: rebuilt from the approved mockup as DOM HTML+CSS. Claude samples colours, measures spacing and proportions from the mockup image, and uses real text from `data/i18n/`, never text baked into images.
- SVG written as text for vector icons and UI frames, redrawn from the approved icon sheet; rasterise in the build (e.g. with resvg or a headless browser).
- Python + Pillow + numpy for noise textures, terrain tiles, gradients, 9-slice panels and UI frames.
- Procedural textures: Perlin/simplex noise, Voronoi, and tileable patterns generated in numpy, tuned to the reference palette.
- Painted single elements that code cannot match: generate them separately with GPT Image 2.5 (`background: transparent`), post-process, ship and log them.

### AI-generated images

- One wrapper: `tools/gen_image.py --provider gemini|openai|nanogpt` (default provider recorded in `000-stack.md`) takes a recipe JSON from `art/recipes/` and writes variants to `build/gen/`. Keys come from `GEMINI_API_KEY`, `OPENAI_API_KEY` or `NANOGPT_API_KEY`, never from files.
- A recipe holds: purpose (`explore`, `reference`, `ui-mockup` or `ship`), model id, the fixed style paragraph from `docs/specs/art-direction.md`, the asset line, reference images from `art/refs/`, size or resolution, quality, n, and post-processing steps.
- Approved references go to `art/refs/`; approved images that ship are post-processed (background removal, palette, scale) and copied to `public/assets/`. Both are recorded in `assets/manifest.json` with provider, model, date, cost and licence.

### Atlases and the asset manifest

- Pack sprites into atlases with a MaxRects packer (Python `rectpack`, or `free-tex-packer-core` in Node). Output PNG + JSON in a format the engine loads (Phaser and PixiJS both read TexturePacker-style JSON).
- Write `assets/manifest.json` listing every generated file with the hash of the recipe that produced it, the references it was built from, and for AI images the provider, model, date, cost and licence. A CI check fails if a code recipe changed but its outputs were not regenerated.

### Visual review loop

- Every art script also writes a contact sheet (all variants and directions in one PNG) to `build/previews/`, and every reference-based build writes a reference-vs-render comparison.
- The agent must open the contact sheet and the comparison with its image-reading tool and check proportions, silhouettes, palette and readability at game scale before reporting the asset as done.
- A separate review agent with an art-direction brief judges the sheet against `docs/specs/art-direction.md` and the approved references.
- The human picks every reference set and approves every hero asset (characters, key art, capsule) before it ships.

## Audio pipeline

Sound effects are parameter sets in JSON or generated clips; music is rendered offline from code or made by hand in Suno and post-processed by scripts. External or generated tracks are allowed only when the project spec says so. Generator choice per audio type is in `AI-ASSET-WORKFLOW.md`.

### Sound effects

- Store each effect as parameters in `audio/sfx/*.json` (ZzFX or jsfxr format). ZzFX can play them live in the browser at almost no size cost, or they can be rendered to files.
- For layered or complex effects (explosions, engines), write Python synthesis with numpy: oscillators, noise, envelopes, filters (scipy.signal), then save with `soundfile`.
- For realistic foley, impacts and ambience, use ElevenLabs Sound Effects through `tools/gen_sfx.py` (prototype via NanoGPT, ship from a paid ElevenLabs plan).
- Name effects after sim events (`unit_died.json`, `ore_mined.json`) so the audio layer maps events to sounds by convention.

### Music

- Default for hero tracks: made by hand in Suno (paid plan, stems from Studio), downloaded as WAV into `audio/external/`, then looped, normalised and encoded by scripts.
- Code route: Python (numpy + soundfile) or SuperCollider in non-interactive mode produces WAV stems; ffmpeg converts them to OGG (Vorbis/Opus) and an AAC/MP3 fallback for browsers that need it. Verify current Safari codec support before shipping.
- Compose as data: tempo, key, chord progression, patterns, mood and instrument presets in `audio/music/*.json`. The same brief drives code rendering and the prompts for Suno, ElevenLabs Music or Lyria.
- Adaptive music: render separate stems (drums, bass, pads, lead) that loop at the same length, and fade stems in or out based on game state. Find loop points with `pymusiclooper`.
- Alternative: Tone.js for live, fully interactive music in the browser. Costs CPU and is harder to test; use only when music must react per beat.
- External or generated tracks go in `audio/external/` with a `LICENSES.md` entry recording source, plan and rights.

### Playback

- A thin Web Audio wrapper: one `AudioContext`, buses for music / SFX / UI / voice with separate volumes, resumed on the first user input (browsers block autoplay).
- Limit simultaneous instances per effect to avoid noise when many units fire at once.

### Review

- An agent cannot listen. The pipeline therefore also outputs a waveform + spectrogram PNG per sound and loudness numbers (peak, LUFS via ffmpeg `loudnorm` analysis). The agent checks for clipping and consistent loudness; the human judges how it sounds.

## Levels and content data

All game content (units, items, parts, prices, maps, dialogue) is data in JSON files validated by zod schemas. Balance changes are data edits, not code edits.

### Content files

- `data/units.json`, `data/parts.json`, `data/economy.json` and so on. One schema per file in `src/data/schemas.ts`.
- Validate at build time (`npm run validate`) and at load time. A typo in a field name fails CI instead of failing silently in game.
- Generate a JSON Schema from the zod schemas (zod v4 has a built-in converter) so editors and other tools get autocomplete and validation too.
- Cross-reference checks: every id an entry refers to must exist (a unit's weapon id, a recipe's ingredient ids).

### Maps and levels

- **LDtk** (default): level editor whose project file is plain JSON, with entities, layers and fields. Agents can generate or edit levels directly in the JSON; the human can still open the file in the editor to tweak by hand.
- **Tiled** (alternative): `.tmj` JSON maps with native Phaser support.
- **Procedural**: seeded generators in `src/sim/gen/` (noise terrain, cellular automata caves, Poisson-disc placement, wave function collapse). Same seed, same map, so maps are testable.
- Every map is rendered to a preview PNG by a script so agents can inspect layout without running the game.

### Text and localisation

- All player-facing strings in `data/i18n/en.json` with keys; other languages as sibling files. No hard-coded UI text in components.

## Testing, bots and performance guards

Quality is enforced by automated checks, not by the human reading code. A feature is done only when all checks pass and the relevant bot report looks sane.

### Test layers

| Layer | Tool | What it covers | When it runs |
| --- | --- | --- | --- |
| Types and lint | `tsc --noEmit`, ESLint | Type errors, forbidden imports (e.g. sim importing render) | Every agent edit (hook) and CI |
| Data validation | zod via `npm run validate` | Content files and cross-references | CI and pre-commit |
| Unit tests | Vitest | Sim rules, economy maths, migrations | CI |
| Property tests | fast-check | Invariants: money never negative, no unit outside map, save → load → save is identical | CI |
| Determinism test | Vitest | Same seed + same input log → identical state hash after N ticks | CI |
| End-to-end | Playwright | Game boots, menus work, a scripted session reaches a milestone, no console errors | CI |
| Visual snapshots | Playwright screenshots | Key screens unchanged unless intended | CI, on demand |
| Performance guard | Playwright + custom metrics | Frame time, draw calls, memory on the production build | CI |
| Asset manifest | `npm run assets:check` | Every file in `public/assets/` is in the manifest with a licence, and lists its references | CI |

### Bots that play the game

- **Pilot bot**: a scripted player that uses the same command API as humans. Runs many seeds headless (Node, sim only) and reports time to each milestone, income per source and failure points. Output: `build/reports/balance.json` plus a short markdown summary.
- **Saboteur bot**: actively hunts exploits — arbitrage loops, softlocks, getting paid twice, negative stock, unreachable states. Every exploit found becomes a regression test before it is fixed.
- Run bots in CI on a small seed set; run large sweeps on demand.

### Performance budgets

- Store budgets in `perf/budgets.json`, e.g. frame time p95 ≤ 16.7 ms, draw calls ≤ 150, JS heap ≤ 300 MB, initial download ≤ 15 MB.
- A Playwright test loads the production build, plays a heavy scripted scene, samples `performance.now()` per frame and reads draw calls from the renderer (`renderer.info` in Three.js), and fails when a budget is exceeded.
- Small regressions add up silently; keep a history file so trends are visible, and run a measured audit every few features.

### Agent hooks

- Configure Claude Code hooks so that after each file edit the type checker and relevant tests run automatically. Agents see failures immediately instead of at the end of a task.

## Repository layout and scripts

Use this layout for every new game so agents know where everything lives without searching.

```
my-game/
├── CLAUDE.md                 # rules for agents (template below)
├── docs/
│   ├── concept.md            # pitch, pillars, core loop, scope
│   ├── specs/                # 000-stack.md, 001-core-loop.md, art-direction.md, audio-direction.md …
│   └── MADE-WITH-AI.md       # running log of workflow lessons
├── .claude/
│   ├── agents/               # subagent definitions (reviewer, art-director, perf-auditor)
│   └── settings.json         # hooks and permissions
├── src/
│   ├── sim/                  # pure deterministic game rules
│   ├── game/                 # loop, input → commands
│   ├── render/               # Phaser / PixiJS / Three.js
│   ├── ui/                   # DOM HUD and menus (rebuilt from approved mockups)
│   ├── audio/                # Web Audio wrapper, event → sound mapping
│   └── data/                 # zod schemas and loaders
├── data/                     # JSON content, maps, i18n
├── art/
│   ├── blender/              # bpy recipe scripts + lib/ (reference planes, rigs, compare)
│   ├── py/                   # Pillow/numpy 2D generators, slicer, palette extractor, atlas packer
│   ├── recipes/              # AI generation recipes (JSON): explore, reference, ui-mockup, ship
│   ├── refs/                 # approved references per group: units/, buildings/, ui/, characters/ …
│   └── palette.json          # extracted from the approved references
├── audio/
│   ├── sfx/                  # ZzFX/jsfxr parameter files and SFX recipes
│   ├── music/                # music-as-data briefs + synth scripts
│   └── external/             # Suno / licensed / generated tracks + LICENSES.md
├── tools/                    # gen_image.py (gemini|openai|nanogpt), gen_sfx.py, post-processing
├── assets/manifest.json      # every shipped asset and reference: hashes, provider, model, cost, licence
├── bots/                     # pilot and saboteur bots
├── tests/
│   ├── unit/
│   ├── e2e/                  # Playwright
│   └── fixtures/saves/       # one save per past version
├── perf/budgets.json
├── public/assets/            # outputs the game loads
└── build/                    # gen/ variants, previews/ (contact sheets, comparisons), reports (git-ignored)
```

### npm scripts

| Script | Does |
| --- | --- |
| `npm run dev` | Vite dev server |
| `npm run build` | Production build to `dist/` |
| `npm run refs:prepare` | Slices approved turnaround sheets into views, normalises them, extracts `art/palette.json` |
| `npm run assets` | Runs all code-based art and audio generators (including Blender recipes built from references), packs atlases, writes the manifest |
| `npm run assets:art -- ship` | Regenerates one asset group only |
| `npm run assets:compare -- ship` | Renders an asset at its reference angles and writes the side-by-side + silhouette comparison |
| `npm run assets:check` | Fails if any recipe hash differs from the manifest or a shipped file lacks a manifest entry |
| `npm run validate` | Validates all JSON content against schemas |
| `npm run check` | Typecheck + lint + validate + unit tests (fast, run constantly) |
| `npm run test:e2e` | Playwright end-to-end tests |
| `npm run bots` | Pilot + saboteur on the CI seed set; writes reports |
| `npm run perf` | Performance guard against `perf/budgets.json` |
| `npm run ci` | Everything CI runs, in CI order |

- Python tools are managed with a pinned `requirements.txt` (or `uv`) in `art/`, `audio/` and `tools/`; the npm scripts call them so there is one entry point.
- AI generation is never part of `npm run assets` or CI: it costs money and is not deterministic. It runs on request (`python tools/gen_image.py art/recipes/<name>.json`) and its approved outputs (references and shipped images) are committed.
- Generated outputs in `public/assets/` are committed (or stored with Git LFS when large), so CI and collaborators do not need Blender or API keys to build the game.

## Claude Code workflow

One coordinator session plans and integrates; fresh subagents do small, file-scoped tasks in parallel; separate reviewer agents check the work. The human designs, decides, picks references and playtests.

### Roles

- **Human**: writes or approves specs, makes design calls, picks reference sets, playtests, approves hero assets, merges.
- **Coordinator** (main Claude Code session): reads the spec, splits it into tasks of roughly one to three files each, assigns file ownership, launches subagents, integrates results, runs `npm run ci`. Starts every new asset group with an exploration and reference round.
- **Builder subagents**: one task each, fresh context, tight brief. They touch only the files they own. Art builders receive the approved reference paths in their brief.
- **Reviewer subagents**: defined in `.claude/agents/` with a deliberately different brief ("find what is wrong", "check against the spec", "art director: compare against the references", "performance auditor"). Agents tend to agree with whatever they are told, so the reviewer never sees the builder's reasoning, only the diff, the spec and the comparison images.

### Choosing the Claude model

- Opus for the coordinator, specs, architecture, art direction and anything where a wrong decision is expensive.
- Sonnet for most builder subagents, including Blender recipes from references, and well-specified implementation tasks.
- Haiku for cheap, mechanical work: file moves, renames, simple data edits, log summaries.
- State the recommended model in each task brief.

### Task brief format

Every subagent brief contains: the goal in one sentence, the spec section it implements, the files it owns, the files it may read (for art: the reference images in `art/refs/`), the files it must not touch, the acceptance checks (which tests must pass, which preview or comparison to look at), the recommended model, and the output expected (a summary plus any open questions).

### Specs

- `docs/specs/NNN-name.md`, numbered in order. Template in the last section.
- Each spec ends with a **Decisions** list. Settled decisions are not reopened by agents.
- Small changes may skip a spec, but any change to rules, economy or save format needs one.

### Git rules (several agents in one repo)

- Each parallel builder works in its own git worktree and branch (`agent/<task-id>`). Never two agents in the same working tree.
- Agents commit only their owned files, in small commits with clear messages. No force-pushes, no rewriting shared history, no edits to `main` directly.
- The coordinator merges branches one at a time and runs `npm run check` after each merge.
- Lockfiles, `CLAUDE.md` and shared config are owned by the coordinator only.

### Useful Claude Code features

- `CLAUDE.md`: loaded automatically; holds the rules (template in the last section).
- Subagents in `.claude/agents/*.md` with their own tools and instructions.
- Hooks in `.claude/settings.json`: run typecheck and tests after edits; block edits to protected paths.
- Skills from the `gamedev-kit` plugin: `/gamedev-kit:new-game`, `/gamedev-kit:game-concept`, `/gamedev-kit:stack-advisor`, `/gamedev-kit:new-asset`. Project-specific skills go in `.claude/skills/`.
- MCP servers at user scope: NanoGPT (asset generation), optionally PixelLab or Retro Diffusion (pixel art), Playwright (drive and screenshot the running game), and a sandboxed Blender MCP for interactive exploration. Headless recipe scripts stay the source of truth.

### Logging what was learned

- `docs/MADE-WITH-AI.md` gets a short entry whenever a workflow problem is solved (what broke, what rule fixed it). Promote recurring lessons into `CLAUDE.md`, and lessons that apply to every game into the `gamedev-kit` repo.

## CI/CD, deployment and packaging

Every push runs the full check suite in GitHub Actions; every merge to `main` deploys the web build automatically. Desktop and Steam builds wrap the same web build.

### CI pipeline (GitHub Actions)

1. Install Node (pinned version) and dependencies with `npm ci`, with caching.
2. `npm run check` — typecheck, lint, data validation, unit and property tests.
3. `npm run assets:check` — generated assets match their recipes and every shipped asset is in the manifest.
4. `npm run build` — production build.
5. `npm run test:e2e` and `npm run perf` against the production build (Playwright with Chromium).
6. `npm run bots` on the CI seed set; upload reports as workflow artefacts.
7. On `main` only: deploy `dist/` to GitHub Pages.

Blender and API keys are not needed in CI because generated assets are committed. If a project chooses to generate code-built assets in CI anyway, download a pinned Blender release in the workflow and cache it. Never call paid AI generators from CI.

### Web release

- **GitHub Pages**: default for development and open-source releases. Set Vite `base` to the repository path.
- **itch.io**: upload with the `butler` CLI from CI for public releases and feedback.
- **Cloudflare Pages**: when a custom domain or faster global delivery is wanted.

### Desktop and Steam

- **Electron + steamworks.js**: default for Steam. Wrap `dist/` in Electron; steamworks.js provides achievements, cloud saves and overlay. Build Windows, macOS and Linux with electron-builder.
- **Tauri**: smaller bundles using the system webview; Steam integration is possible through community Rust bindings but takes more work. Test rendering on each OS because webviews differ.
- Keep platform code behind one interface (`src/platform/`) with a web implementation and a desktop implementation, so the game code stays identical.
- Upload builds to Steam with SteamPipe (`steamcmd`) from CI on tagged releases. Fill in Steam's AI content disclosure from `assets/manifest.json`, including the reference images (see AI-ASSET-WORKFLOW.md).

### Versioning

- Semantic version in `package.json`, shown in the main menu, included in every save and every bug report.

## Stack recipes by game type

Start from the closest recipe below and adjust. Every recipe shares the same principles, the reference-first art step, test layers, workflow and CI; only the rendering, build routes and simulation choices differ.

| Game type | Rendering | Art (always after a reference round) | Simulation notes | Levels |
| --- | --- | --- | --- | --- |
| 2D pixel-art god sim / sandbox | PixiJS (or Phaser) at low internal resolution | Nano Banana style refs → Pillow tiles + palette quantization; Blender creatures rendered small, or PixelLab / Retro Diffusion with the refs attached | Cellular grid, chunked updates, many agents → consider bitECS | Procedural, seeded |
| Classic RTS (2D sprites) | Phaser or PixiJS | Unit and building turnarounds → Blender units rendered in 8–16 directions, team-colour masks; Tripo from refs for organic units; HUD rebuilt from mockups | Fixed tick, flow-field pathfinding, fog of war on a grid | LDtk maps + procedural skirmish maps |
| Top-down 3D action / space | Three.js, orthographic or low-angle perspective camera | Turnarounds → Blender models exported as GLB; procedural materials; bloom post-processing | Rigid bodies (custom or Rapier), instanced meshes for debris and asteroids | Procedural sectors |
| Turn-based strategy / wargame | Phaser or PixiJS (map) + DOM UI (panels, orders) | Map and counter mockups → Pillow/SVG counters, map tiles and icons; unit turnarounds → Blender miniatures | Turn resolution as pure functions; full undo through command history | LDtk or hand-authored JSON scenarios |
| Story / management sim (e.g. fighter manager) | Phaser or DOM-heavy UI | Nano Banana portraits shipped directly with a style bible; robot turnarounds → Blender; UI rebuilt from mockups | Event and stat system as pure functions; save-heavy | JSON story beats and events |
| 2D side-view pixel story / management game (Punch Club-style) | Phaser at a fixed low base resolution (e.g. 480×270 or 640×360, integer-scaled), nearest-neighbour | Character and location refs from Nano Banana → characters as rigged Blender models rendered side-on at low resolution, toon-shaded, no anti-aliasing, quantised to the palette (the "3D to pixel" method Dead Cells is known for); robots via Route A, humans via Route B; backgrounds as low-res Blender scenes or PixelLab / Retro Diffusion with the ref attached, then `unfake`; optional PixelLab clean-up pass on hero frames; UI rebuilt as HTML/CSS with a pixel font | Day/time-slot scheduler, stat decay and training as pure functions; fights as a deterministic turn-based or auto-battle resolver; save-heavy | Hand-authored JSON locations, events and story beats |
| Puzzle / casual | Phaser or Canvas 2D | Mockups → SVG and Pillow; minimal Blender | Pure state machine; every level solvable is checked by a solver bot | JSON levels + generator |
| Card / deck-builder | DOM + CSS (cards as HTML) | Card-frame mockups → SVG frames; illustrations shipped from GPT Image / Nano Banana or rendered in Blender from refs | Seeded shuffle; simulation bots for balance win rates | Card data in JSON |

For every recipe, the first spec (`000-stack.md`) records: the chosen row, the pinned versions of Node, Blender and Python, the target platforms, the input method (keyboard + mouse, touch, controller), the performance budgets, the reference route (Gemini direct, OpenAI direct or NanoGPT) and main reference model, and the asset decisions from the checklist in AI-ASSET-WORKFLOW.md.

## Known pitfalls

These problems recur in agent-built games; each has a rule that prevents it.

| Pitfall | Prevention rule |
| --- | --- |
| Several agents in one working tree overwrite each other's changes | One worktree and branch per agent; coordinator merges one at a time |
| Agents agree with whatever is suggested; self-review finds nothing | Reviews by a separate agent with an adversarial brief that sees only the diff, spec and comparison images |
| Long sessions drift and forget earlier decisions | Fresh agent per task; decisions live in specs, not in chat history |
| Settled design choices get re-argued | Decisions list at the end of each spec; `CLAUDE.md` says not to reopen them |
| Small performance costs pile up unnoticed | Budgets enforced in CI plus a periodic measured audit |
| Sim logic leaks into rendering (or reverse), breaking bots and saves | Lint rule forbidding imports from `render/`, `ui/`, `audio/` inside `sim/` |
| Hidden randomness breaks determinism | Lint rule banning `Math.random` and `Date.now` in `sim/`; determinism test in CI |
| Code-built art looks generic or "programmer art" | Reference-first: no final asset without an approved reference; comparison image required |
| AI references are pretty but unusable for modelling (perspective, dramatic light, mismatched views) | Ask explicitly for orthographic turnarounds, flat light, plain background, one shared scale and ground line |
| Blender build drifts from the reference or loops forever | Silhouette comparison after each round; stop after 3–5 rounds and ask the human |
| Generated art looks fine in code but wrong on screen | Mandatory contact sheet and in-game screenshot that the agent views before finishing |
| Inconsistent art style across assets | One palette file (from the refs), one lighting rig, one camera rig, one style bible in `art/refs/`, shared by all recipes |
| UI text baked into images, impossible to translate | UI rebuilt as HTML/SVG with strings from `data/i18n/`; mockups are design specs only |
| AI generation costs run away | One API key per game with a USD-per-day cap; dry-run estimates; cost logged per call; n=1 outside exploration |
| An asset ships under a non-commercial licence | Licence field required in the manifest; `assets:check` fails without it |
| Blender API breaks after an update | Pin the Blender version; upgrade deliberately in its own task |
| Old saves stop loading | Versioned saves, one migration per version, fixture saves tested in CI |
| Economy exploits found by players | Saboteur bot; every exploit becomes a regression test |
| Audio blocked or silent on first load | Resume the `AudioContext` on the first user input |
| Agent claims a task is done without running checks | Hooks run checks automatically; brief requires pasting check results |

## Templates

Copy these into a new repository and fill in the placeholders in angle brackets. The `gamedev-kit` plugin's `new-game` skill does this automatically.

### CLAUDE.md

```markdown
# <Game name> — rules for agents

Stack and principles: GAME-STACK.md (gamedev-kit knowledge). Chosen stack: docs/specs/000-stack.md. Concept: docs/concept.md.

## Roles
- The human designs, picks references and playtests. Agents build. Ask the human when a design choice is not in a spec.
- Decisions recorded in docs/specs/* are final. Do not reopen them.

## Architecture
- src/sim is pure and deterministic: no imports from render/, ui/, audio/, no DOM, no Math.random, no Date.now.
- Players and bots act only through sim commands.
- All content is JSON in data/, validated by schemas in src/data/schemas.ts.
- All art and audio come from scripts in art/, audio/ and tools/. Never hand-edit files in public/assets/.

## Art: reference first (default for every asset group)
- Before building any final visual asset, generate options with <Nano Banana 2.1 | GPT Image 2.5> via tools/gen_image.py (provider: <gemini | openai | nanogpt>), show the human a contact sheet, and wait for a pick.
- Then generate reference sheets (orthographic turnarounds, UI mockups) from the pick; approved ones go to art/refs/<group>/.
- Build assets to match the references: Blender recipes in art/blender/ (Route A), image-to-3D + Blender (Route B), or HTML/SVG/Pillow for UI (Route C).
- Run `npm run assets:compare -- <asset>` and read the comparison before reporting done. Max 3-5 rounds, then ask the human.
- Greybox placeholders without references are allowed only before the vertical slice.

## Assets
- Follow AI-ASSET-WORKFLOW.md for which generator to use per asset type.
- Every AI image (reference or shipped) has a recipe in art/recipes/ and an entry in assets/manifest.json (provider, model, date, cost, licence); shipped assets list the references they were built from.
- Read the contact sheet, comparison or spectrogram before reporting an asset done. The human approves hero assets.
- Never print or commit API keys (GEMINI_API_KEY, OPENAI_API_KEY, NANOGPT_API_KEY). Ask before any generation run estimated above $<budget>.

## Working rules
- Touch only the files your task brief assigns to you.
- Work in your own git worktree and branch (agent/<task-id>). Never commit to main. Never force-push.
- Run `npm run check` before reporting done and paste the result.
- After changing gameplay, run `npm run bots` and summarise the report.
- Every exploit or bug fixed gets a regression test.
- Save format changes: bump the version, add a migration, add a fixture save.

## Pinned versions
- Node <version>, Blender <version>, Python <version>
```

### Feature spec

```markdown
# NNN — <Feature name>

## Goal
One or two sentences: what the player can do after this ships.

## Player experience
What the player sees, does and feels. First-15-minutes impact.

## Rules
Exact mechanics, numbers and edge cases. Data lives in data/<file>.json.

## Art and references
Which asset groups this needs, which approved references in art/refs/ apply, and which still need an exploration round.

## Out of scope
What this spec deliberately does not cover.

## Tasks and file ownership
| Task | Owner files | Depends on | Model |
| --- | --- | --- | --- |

## Acceptance checks
- Unit / property tests that must exist and pass
- Bot report expectations (e.g. milestone X reached within N minutes on 90% of seeds)
- Visual check: which preview, comparison or screenshot to inspect
- Performance: stays within perf/budgets.json

## Decisions
- <date> — <decision> — <reason>

## Open questions
- <question for the human>
```

### Blender helper: reference planes

Loads the sliced reference views as image empties on the front (XZ), side (YZ) and top (XY) planes, bottom-centred on the origin, so a recipe can build geometry against them. Put it in `art/blender/lib/refs.py`. The empties are hidden from renders.

```python
import math
from pathlib import Path

import bpy

VIEW_ROTATIONS = {
    "front": (math.pi / 2, 0.0, 0.0),          # XZ plane, seen from -Y
    "side": (math.pi / 2, 0.0, math.pi / 2),   # YZ plane, seen from +X
    "top": (0.0, 0.0, 0.0),                    # XY plane, seen from +Z
}


def add_reference(image_path: Path, view: str, size: float) -> bpy.types.Object:
    """size = real-world length of the image's longest side in Blender units."""
    img = bpy.data.images.load(str(image_path), check_existing=True)
    empty = bpy.data.objects.new(f"ref_{view}", None)
    empty.empty_display_type = "IMAGE"
    empty.data = img
    empty.empty_display_size = size
    # Bottom-centred for front/side so the ground line sits at z = 0; centred for top.
    empty.empty_image_offset = (-0.5, -0.5) if view == "top" else (-0.5, 0.0)
    empty.rotation_euler = VIEW_ROTATIONS[view]
    empty.use_empty_image_alpha = True
    empty.color[3] = 0.5                       # semi-transparent in the viewport
    empty.hide_render = True
    bpy.context.scene.collection.objects.link(empty)
    return empty


def add_reference_set(ref_dir: Path, size: float) -> dict:
    """Loads front.png, side.png and top.png from a sliced reference folder if present."""
    return {
        view: add_reference(ref_dir / f"{view}.png", view, size)
        for view in VIEW_ROTATIONS
        if (ref_dir / f"{view}.png").exists()
    }
```

### Comparison script: reference vs. render

Run after an orthographic render of the same view (transparent background). Writes a side-by-side plus silhouette overlay to `build/previews/` and prints the silhouette IoU. Put it in `art/py/compare.py`. It accepts either a transparent sliced view (from `slice_refs.py`) or a reference on a flat background colour.

```python
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def silhouette_from_reference(img: Image.Image, tol: int = 30) -> np.ndarray:
    rgba = np.asarray(img.convert("RGBA"))
    if (rgba[:, :, 3] < 255).any():          # sliced views from slice_refs.py are transparent
        return rgba[:, :, 3] > 10
    a = rgba[:, :, :3].astype(int)
    bg = np.median(np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]), axis=0)
    return np.abs(a - bg).sum(axis=2) > tol


def silhouette_from_render(img: Image.Image) -> np.ndarray:
    return np.asarray(img.convert("RGBA"))[:, :, 3] > 10


def crop_to(mask: np.ndarray, img: Image.Image, height: int):
    ys, xs = np.nonzero(mask)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    c_img = img.crop(box)
    c_mask = Image.fromarray(mask[box[1]:box[3], box[0]:box[2]].astype(np.uint8) * 255)
    w = round(c_img.width * height / c_img.height)
    return c_img.resize((w, height), Image.LANCZOS), c_mask.resize((w, height), Image.NEAREST)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ref", required=True)
    p.add_argument("--render", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--height", type=int, default=512)
    a = p.parse_args()

    ref, ren = Image.open(a.ref), Image.open(a.render)
    ref_img, ref_m = crop_to(silhouette_from_reference(ref), ref, a.height)
    ren_img, ren_m = crop_to(silhouette_from_render(ren), ren, a.height)

    w = max(ref_m.width, ren_m.width)
    rm = np.zeros((a.height, w), bool)
    nm = np.zeros((a.height, w), bool)
    rm[:, (w - ref_m.width) // 2:(w - ref_m.width) // 2 + ref_m.width] = np.asarray(ref_m) > 0
    nm[:, (w - ren_m.width) // 2:(w - ren_m.width) // 2 + ren_m.width] = np.asarray(ren_m) > 0
    iou = float((rm & nm).sum() / max((rm | nm).sum(), 1))

    overlay = np.full((a.height, w, 3), 255, np.uint8)
    overlay[rm & ~nm] = (230, 60, 60)    # only in reference: missing in the build
    overlay[nm & ~rm] = (60, 110, 230)   # only in render: extra in the build
    overlay[rm & nm] = (90, 90, 90)      # match

    sheet = Image.new("RGB", (ref_img.width + ren_img.width + w + 40, a.height), "white")
    sheet.paste(ref_img.convert("RGB"), (0, 0))
    sheet.paste(ren_img.convert("RGBA"), (ref_img.width + 20, 0), ren_img.convert("RGBA"))
    sheet.paste(Image.fromarray(overlay), (ref_img.width + ren_img.width + 40, 0))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(a.out)
    print(json.dumps({"silhouette_iou": round(iou, 3), "out": a.out}))


main()
```

Red areas are parts the build is missing, blue areas are parts it has too much of. An IoU above roughly 0.85 usually means the proportions are right; the remaining judgement (details, colour, appeal) is done by reading the image, and by the human for hero assets.

### Blender sprite recipe skeleton

Renders a simple unit in N directions with a transparent background and writes a frame map. Run with `blender --background --factory-startup --python art/blender/sprite_unit.py -- --out build/art/tank --directions 8`. It expects `art/palette.json` with linear RGB values in 0–1, e.g. `{"hull": [0.2, 0.3, 0.15], "metal": [0.5, 0.5, 0.55]}`. In a real recipe, call `add_reference_set(Path("art/refs/units/tank"), size=...)` from the helper above before building, and size and place the primitives to match the reference views.

```python
import argparse
import json
import math
import sys
from pathlib import Path

import bpy


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--directions", type=int, default=8)
    p.add_argument("--size", type=int, default=128)
    return p.parse_args(argv)


def reset_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def make_material(name, rgb):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.6
    return mat


def build_model(palette):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.25))
    hull = bpy.context.active_object
    hull.scale = (1.0, 0.6, 0.25)
    bevel = hull.modifiers.new("bevel", "BEVEL")
    bevel.width = 0.05
    bevel.segments = 2
    hull.data.materials.append(make_material("hull", palette["hull"]))

    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.08, depth=0.7, location=(0.4, 0, 0.5), rotation=(0, math.pi / 2, 0)
    )
    barrel = bpy.context.active_object
    barrel.data.materials.append(make_material("metal", palette["metal"]))

    root = bpy.data.objects.new("root", None)
    bpy.context.scene.collection.objects.link(root)
    hull.parent = root
    barrel.parent = root
    return root


def setup_scene(size):
    scene = bpy.context.scene

    cam_data = bpy.data.cameras.new("cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 2.5
    cam = bpy.data.objects.new("cam", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (0, -4, 4)
    cam.rotation_euler = (math.radians(45), 0, 0)
    scene.camera = cam

    sun_data = bpy.data.lights.new("sun", "SUN")
    sun_data.energy = 3.0
    sun = bpy.data.objects.new("sun", sun_data)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))

    # Engine identifier differs between Blender versions.
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue

    scene.render.resolution_x = size
    scene.render.resolution_y = size
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"


def render_directions(root, out_dir, n):
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    for i in range(n):
        root.rotation_euler = (0, 0, 2 * math.pi * i / n)
        path = out_dir / f"dir_{i:02d}.png"
        bpy.context.scene.render.filepath = str(path.resolve())
        bpy.ops.render.render(write_still=True)
        frames.append(path.name)
    meta = {"directions": n, "frames": frames}
    (out_dir / "frames.json").write_text(json.dumps(meta, indent=2))


def main():
    args = parse_args()
    palette_path = Path(__file__).resolve().parents[1] / "palette.json"
    palette = json.loads(palette_path.read_text())
    reset_scene()
    root = build_model(palette)
    setup_scene(args.size)
    render_directions(root, Path(args.out), args.directions)


main()
```

Next steps for a real pipeline: move `reset_scene`, `make_material` and `setup_scene` into `art/blender/lib/`, load the reference set before `build_model`, add an orthographic front/side render step that feeds `art/py/compare.py`, add a contact-sheet step (Pillow) and an atlas packer, and record the script hash and its references in `assets/manifest.json`.
