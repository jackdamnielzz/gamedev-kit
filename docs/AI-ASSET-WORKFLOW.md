# AI Asset Workflow for Claude-Driven Game Development

20 October 2026 · Niels. Living version: the claude.ai doc "AI Asset Workflow for Claude-Driven Game Development". Prices and model versions change monthly: re-check provider pages before committing a budget.

**Update 20 October 2026:** the **reference-first pipeline** (AI image model makes reference sheets and UI mockups → the human picks → Claude builds the real asset in Blender or code from those references) is now the default art pipeline for every game. See the section "The default pipeline: AI references → Blender".

## Summary

Claude Code directs and builds; AI image models design. For every game, Claude starts the art work by generating reference images with an AI image model (Nano Banana 2.1 by default, GPT Image 2.5 as the alternative), lets the human pick, and then builds the in-game assets in Blender (driven by Python) or in code, matching the chosen references. Building assets "blind" from a text description is no longer the default.

NanoGPT is the default gateway for one key and one MCP server; the Gemini API (Google) and the OpenAI API are equal, direct alternatives for the reference images, with direct accounts elsewhere where rights, price or features demand it.

| Asset type | Default tool | Route | Why |
| --- | --- | --- | --- |
| **Concept art, reference sheets, turnarounds** | **Nano Banana 2.1** (Pro for complex scenes); GPT Image 2.5 as alternative | Gemini API direct, OpenAI API direct, or NanoGPT | **Start of every art pipeline**; strong multi-reference consistency |
| **UI, HUD, menu mockups** | **Nano Banana 2.1 / GPT Image 2.5 mockups → Claude rebuilds in SVG / HTML+CSS / Pillow** | Generate via API; build in repo | Human picks a look from options; shipped UI stays editable code |
| Icons | GPT Image 2.5 reference sheet → Claude redraws as SVG | API + code | Crisp, scalable, consistent |
| Tiles, effects, procedural textures | Claude: numpy, shaders (palette and look taken from the approved references) | Code in repo | Deterministic |
| **Mechanical units, vehicles, buildings, props (3D or pre-rendered sprites)** | **AI reference sheet → Claude builds in Blender `bpy`** | API + code in repo | Exact control, matches the chosen design |
| **Organic 3D models (creatures, characters)** | **AI reference sheet → Tripo / Meshy image-to-3D → Blender clean-up and render** | NanoGPT or direct | Code alone cannot sculpt organic shapes |
| Painted 2D props and cut-out art (2D games) | GPT Image 2.5 Flare | NanoGPT or OpenAI direct | Native transparency, cheap |
| Consistent characters, portraits (2D story games) | Nano Banana 2.1 / Pro + style refs | Gemini direct or NanoGPT | Strongest multi-reference |
| Bulk assets in one style | FLUX.2 / Klein LoRA trained on approved references | fal.ai | Style lock-in at scale |
| Key art, Steam capsule | GPT Image 2.5 or Nano Banana Pro, or a human artist | NanoGPT or direct | Highest stakes, human final say |
| Pixel-art characters, animation | PixelLab or Retro Diffusion (fed with the approved references) | Their own MCP | Real pixel grid, directions |
| Retro and UI sound effects | ZzFX / jsfxr | Code in repo | No licence or disclosure |
| Realistic sound effects | ElevenLabs Sound Effects v2 | NanoGPT (prototype), direct (ship) | Loop flag, commercial on paid plan |
| Hero music tracks | Suno v6 Premier, by hand | Manual download | Best quality, stems |
| Variations, stingers | ElevenLabs Music or Lyria | Direct API | Agent-callable, indie licence |
| Voice | ElevenLabs v4 / Multilingual v2 | Direct | Quality, Dutch, clear rights |
| Trailer clips | Veo 3.1 Fast | NanoGPT | Cheaper than direct |

Four rules matter most: start every visual asset from AI reference images the human has picked; generate on paid commercial plans (never the NanoGPT subscription or free tiers); log every asset and every reference in `assets/manifest.json` for the Steam AI disclosure; and let the human approve every reference set, hero asset and track.

## Guiding principles

Claude Code is the director, the builder and the pipeline; AI image models are the concept artists. Claude writes prompts, calls generators through APIs, CLIs or MCP servers, reads the results, and then builds the real assets in Blender and code.

**What Claude does itself**

- Prompt writing from the art direction, reference-sheet generation runs, contact sheets for the human to pick from.
- Art as code: SVG, Canvas, shaders, Blender Python (`bpy`) and Pillow/numpy scripts, built to match the approved references. Deterministic, versionable, consistent.
- Audio as code: ZzFX/jsfxr parameter files and numpy synthesis for SFX; music-as-data rendered offline.
- Post-processing: background removal calls, palette extraction and quantisation, slicing, atlas packing, loudness normalisation, looping, format conversion.
- Visual review: Claude reads PNGs, contact sheets, side-by-side comparisons (reference vs. Blender render) and screenshots, and iterates on them.

**What Claude cannot do**

- Generate raster images, audio or video natively (that is what the image models are for).
- Listen. Audio review relies on waveform and spectrogram PNGs, loudness numbers and the human's ears.
- Judge taste reliably. The human picks reference sets and approves every hero asset.

**The push rule (applies to every game)**

Claude proactively proposes and runs the reference-first pipeline at the start of each game's art work and for every new asset group (units, buildings, UI, characters). It does not wait to be asked, and it does not start modelling or drawing from a text description alone. The only exceptions are pure placeholders (greybox cubes, debug UI) and assets the human explicitly says to build without references. If no image API key is available, Claude says so and asks the human to set one up instead of silently skipping the step.

**Rules for every pipeline**

1. Every asset has a recipe in the repo: the reference images it was built from, the prompt and model id that made those references, the Blender or code script that builds the asset, and the post-processing steps. The generated file is a build artefact.
2. One style source of truth: `docs/specs/art-direction.md`, `art/palette.json` (extracted from the approved references), the approved reference images in `art/refs/`, and an audio brief in `docs/specs/audio-direction.md`.
3. Generate in batches of variants, then let the human select. Never build on a first take nobody chose.
4. Every visual step writes a contact sheet or a side-by-side comparison; every audio step writes a spectrogram and a loudness report. Claude reads them before reporting done.
5. Record provider, model, date and licence per asset and per reference in `assets/manifest.json`, so the Steam AI disclosure and any licence questions can be answered later.
6. Wrap each provider behind one small script (`tools/gen_image.py` with a `--provider gemini|openai|nanogpt` switch, `tools/gen_sfx.py`) so a model can be swapped without touching the rest of the pipeline.

## The default pipeline: AI references → Blender

This is the pipeline Claude uses for every game. An AI image model produces design options and reference sheets; the human picks; Claude then builds the actual game asset in Blender (or SVG/HTML for UI) using the chosen images as its visual target, and checks its result against them.

**Why this works better than either approach alone.** AI image models are strong at design and look, but their output is a flat picture: no clean geometry, no consistent views, no animation-ready parts, no reliable transparency or palette. Claude in Blender is strong at exact, consistent, reusable geometry, but weak at inventing an appealing design from words. Combining them gives a designed look (from the model) with controllable, consistent, animatable assets (from Blender). A side benefit: the shipped asset is built by a script, not a raw AI image, which keeps the style consistent and gives more human-directed authorship than shipping the raw picture (see the legal section; disclosure is still required).

### Overview

```
0 Art direction      docs/specs/art-direction.md: genre, mood, camera angle, palette idea, 3-5 visual keywords
        ↓
1 Explore            Image model: 4-8 style options per asset group (units, buildings, UI, characters)
        ↓
2 Human picks        Contact sheet in build/previews/; the human chooses and comments
        ↓
3 Reference sheets   Image model, with the chosen image attached: orthographic turnaround
                     (front / side / back / top), detail callouts, colour swatches; UI screen mockups
        ↓
4 Approve + extract  Approved sheets → art/refs/<group>/; palette.json extracted from them
        ↓
5 Build              Route A: Blender bpy from primitives, with references loaded as image planes
                     Route B: image-to-3D (Tripo / Meshy) → Blender clean-up
                     Route C: UI and icons rebuilt in SVG / HTML+CSS / Pillow
        ↓
6 Compare            Render at the reference's camera angle; side-by-side + silhouette overlay PNG;
                     Claude reads it, fixes differences; max 3-5 rounds, then ask the human
        ↓
7 Output             Sprites (8/16 directions), GLB for Three.js, atlases, UI code
        ↓
8 Verify + log       In-game screenshot, human approval of hero assets, manifest entry
```

### Step 0–2: art direction and exploration

- Claude drafts `docs/specs/art-direction.md` with the human: genre, mood, era, camera (top-down, isometric 30°, side view), target sprite size or polygon budget, and 3–5 visual keywords. This text becomes the fixed style paragraph in every prompt.
- Exploration runs generate 4–8 options per asset group with clearly different styles (for example "chunky low-poly toy look", "gritty painted realism", "clean cel-shaded"). One call per option, n=1, so costs stay small.
- Claude assembles a labelled contact sheet (Pillow) in `build/previews/explore_<group>.png`, reads it, and presents it to the human with a one-line description per option. The human picks one (or mixes: "the shape of B, the colours of D").

### Step 3: reference sheets the Blender stage can use

The images that feed Blender must be designed for modelling, not for beauty. Claude asks the model for:

- **Orthographic turnaround sheets** for every unit, vehicle, building and character: front, side, back and top views on one sheet, same scale, aligned on a shared ground line, no perspective, flat even lighting, plain neutral background (mid-grey or magenta `#FF00FF` for easy keying), no cast shadows, no text.
- **Detail callouts**: close-ups of parts that matter (turret, wheels, face, logo), plus a row of flat colour swatches.
- **In-game-view mockup**: the asset at the real camera angle and real on-screen size, to check readability.
- **UI mockups**: full screens (main menu, HUD over a game scene, inventory, dialogue box) at the target resolution, plus a sheet of separate UI elements (buttons in normal / hover / pressed state, panels, frames, icon set) on a plain background.

Always attach the chosen exploration image (and earlier approved references) to the call, and repeat the full style paragraph: the models have no memory between calls. Nano Banana 2.1 accepts up to 14 reference images per call (up to 4 characters and 10 objects); GPT Image 2.5 up to 16.

Prompt template for a turnaround sheet:

```
<fixed style paragraph from art-direction.md>
Character/model turnaround reference sheet of <asset description>, matching the attached design exactly.
Four orthographic views in one row: front, left side, back, top. Same scale in every view,
aligned on one ground line, no perspective, flat even studio lighting, no cast shadows,
plain flat #808080 background, no text, no labels. Below the views: a row of 6 flat colour swatches
taken from the design. Clean readable shapes suitable for 3D modelling.
```

### Step 4: approve and extract

- The human approves the reference sheets. They are copied to `art/refs/<group>/<asset>_turnaround.png` (and `_detail.png`, `_ingame.png`) and listed in the manifest as references (provider, model, prompt hash, date, cost).
- A Pillow script slices the turnaround into separate view images (`front.png`, `side.png`, `back.png`, `top.png`) by detecting the background gaps, crops each tight, and normalises them to the same height.
- A palette script runs k-means (numpy or scikit-learn) on the approved references and writes the dominant colours to `art/palette.json` (converted to linear RGB for Blender). Claude names the colours (`hull`, `trim`, `glass`, `skin` …) with the human.

### Step 5: build in Blender

Claude installs nothing in the game itself; the human installs Blender once and pins the version in `000-stack.md`. Claude drives it headless (`blender --background --factory-startup --python art/blender/<recipe>.py -- <args>`), and may run an interactive Blender session through the official or a sandboxed Blender MCP for exploration, but the committed recipe script stays the source of truth.

**Route A — model from primitives (default for mechanical and architectural assets).**

1. The recipe loads the sliced views as reference image empties: front view on the XZ plane, side view on the YZ plane, top view on the XY plane, scaled so one Blender unit equals the asset's real size. This is the classic modelling-sheet setup, done by script.
2. Claude reads the reference images itself (it can see PNGs) and writes the geometry: primitives plus modifiers (bevel, mirror, array, boolean, solidify, subdivision), sized and placed to match the silhouettes in the views. Parts that move (turret, wheels, arms) are separate objects with correct pivots, so they can be animated.
3. Materials come from `art/palette.json`; the shared lighting and camera rig from `art/blender/lib/` gives every asset the same look.
4. Optional texture detail: project the front or side reference onto the mesh (UV project from view, or a texture-paint bake) for decals and painted detail, or generate a separate tileable texture with the image model. Projected AI pixels are shipped content and must be disclosed.

**Route B — image-to-3D, then Blender (default for organic assets).** Send the approved front view (or the full turnaround where the service supports multi-view input) to Tripo or Meshy, remesh to the polygon budget, auto-rig if needed, then import the GLB in a Blender recipe that applies the project palette materials, lighting rig and scale, and renders it exactly like Route A assets. Details in "3D generation".

**Route C — UI and icons rebuilt as code.** Claude treats the approved UI mockup as a design spec: it measures layout, spacing, colours (sampled with Pillow), corner radii and font style from the image, then rebuilds the screen as DOM HTML+CSS (default UI layer), SVG frames and icons, or Pillow-rendered 9-slice panels. Text is always real text from `data/i18n/`, never baked into an image. Painted elements that code cannot reproduce well (an ornate frame, a background illustration) may be generated separately as clean single elements with GPT Image 2.5 (transparent background), post-processed and shipped as assets, logged in the manifest.

### Step 6: compare and iterate

After each build, the recipe renders the asset from the same orthographic angles as the reference views (plus the in-game camera angle), and a Pillow script writes `build/previews/<asset>_compare.png`: reference and render side by side, plus a silhouette overlay (reference silhouette in one colour, render silhouette in another) and an optional silhouette IoU score. Claude reads the comparison, lists the differences (proportions, missing parts, colour drift), fixes the script and re-renders. After 3–5 rounds without convergence it stops and shows the human the best result with the remaining differences, rather than looping.

The goal is a faithful, game-ready interpretation, not a pixel copy: simplify details that will not read at game scale, and keep the silhouette and colour blocking right.

### Step 7–8: output, verify, log

- Outputs follow GAME-STACK.md: 8 or 16 directions per unit with a transparent background, animation frames, team-colour masks, GLB exports, packed atlases, UI code.
- Claude takes an in-game screenshot (Playwright) and checks readability at real size; the human approves hero assets.
- The manifest entry for the shipped asset records the build script hash, the references it was built from (with their provider and model), whether AI pixels were projected into it, and the licence.

### Getting the images: three routes

All three routes are fine; pick one per game in `000-stack.md` and keep the key in an environment variable, never in the repo. `tools/gen_image.py` hides the difference behind a `--provider` switch.

| Route | Key (environment variable) | Model ids (October 2026) | Notes |
| --- | --- | --- | --- |
| Gemini API direct (Google) | `GEMINI_API_KEY` from Google AI Studio, on a project with billing enabled | `gemini-nano-banana-2.1` (default), `gemini-3-pro-image` (Nano Banana Pro), `gemini-3.1-flash-image` (Nano Banana 2) | Google documents image generation for 2.1 on its Interactions API; implement the wrapper against the current "Image generation" page and verify the request shape on the first call. 1K/2K/4K output, up to 14 references, configurable thinking level, Batch API supported. No free API tier for 2.1 (secondary source); transparency not documented |
| OpenAI API direct | `OPENAI_API_KEY` | `gpt-image-2.5-flare` (fast default), `gpt-image-2.5-sunburst` | Images API; `background: "transparent"` supported (PNG/WebP); up to 16 reference images; mask editing |
| NanoGPT | `NANOGPT_API_KEY` | `nano-banana-2`, `nano-banana-pro`, `openai/gpt-image-2.5/flare/text-to-image` (+ `/edit`), `gpt-image-2` | One balance for everything; see NANOGPT-API.md. Check the catalogue for a Nano Banana 2.1 id before assuming it is listed. `gpt-image-2` on NanoGPT has no `background` parameter |

Practical notes:

- Ask for one image per call, inspect it, then decide; batches of variants only in the exploration step.
- For Nano Banana (no documented transparency), generate on a flat key colour and remove the background with a keying script or BiRefNet. Reference sheets do not need transparency at all.
- Downscale reference images to about 1024 px and under 1.5 MB before attaching them (NanoGPT rejected a 3.7 MB 2048-px PNG).
- Log `cost` per call and keep a per-game daily cap; exploration plus reference sheets for a small game usually costs a few dollars.

### When to deviate

- **Pixel art:** the references still come from Nano Banana or GPT Image; the sprites then come from Blender rendered small and quantised, or from PixelLab / Retro Diffusion with the reference attached. Never ship a general model's "pixel art" directly.
- **Painted 2D games (story, portraits, card art):** the approved image itself is the asset (Route "direct"), post-processed and logged. Blender is used only for mechanical parts or consistency renders.
- **Placeholders:** greybox without references is fine during prototyping (the indie guide's gate 1); the reference pipeline starts with the vertical slice.

## Image and 2D art

Nano Banana 2.1 is the default for exploration and reference sheets (strong consistency across many references); GPT Image 2.5 Flare is the default when an image itself ships and needs a transparent background. Once the style is settled, a FLUX LoRA locks it in for bulk generation.

### Models (API, October 2026)

| Model | Price per image (1024²) | Transparent PNG | References for consistency | Editing | Best for |
| --- | --- | --- | --- | --- | --- |
| [GPT Image 2.5 Flare / Sunburst](https://developers.openai.com/api/docs/pricing) | about $0.006 low, $0.013 medium, $0.053 high | Yes, native | Up to 16 inputs | Yes, mask optional | Props, UI elements, icons, anything cut out; reference sheets (alternative) |
| [Nano Banana 2.1](https://ai.google.dev/gemini-api/docs/models/gemini-nano-banana-2.1) (`gemini-nano-banana-2.1`) | about half of Nano Banana 2 at the same resolution; check the [pricing page](https://ai.google.dev/gemini-api/docs/pricing) | Not documented | Up to 14 (4 characters + 10 objects) | By prompt, mask-style editing | **Default for exploration, turnarounds, UI mockups** |
| Nano Banana 2 (`gemini-3.1-flash-image`) | $0.034 (1K), $0.05 (2K) | Not documented | 10 object + 4 character | By prompt | Fallback where 2.1 is not offered (e.g. some aggregators) |
| Nano Banana Pro (`gemini-3-pro-image`) | $0.134 (1K/2K), $0.24 (4K) | Not documented | 6 object + 5 character + 3 style | By prompt | Key art, complex scenes, dense UI mockups with text |
| [FLUX 3 Image](https://docs.bfl.ml/release-notes) (1 October 2026) | about $0.048 | Not stated | Up to 10 | Yes | Detailed illustration |
| [FLUX.2 pro](https://bfl.ai/pricing) | $0.03 per MP | — | Max version up to 10 | Yes | Bulk, LoRA style lock |
| Seedream 5.0 Pro | about $0.045 | — | Multi-reference | Yes | Cheap volume |
| [Recraft V4.1](https://www.recraft.ai/docs/recraft-models/recraft-V4) | $0.035 raster, $0.08 SVG vector | Separate $0.01 call | No custom styles | Yes | Vector icons, logos |
| Ideogram 3 / 4.5 | Varies | Ideogram V3 Transparent | — | — | Text and titles in images |
| Midjourney | No official API | — | — | — | Not usable from Claude Code |

Note: on NanoGPT, `gpt-image-2` does not support `background`; GPT Image 2.5 does (see NANOGPT-API.md). GPT Image 1 is deprecated on 23 October 2026. Every Gemini image carries a SynthID watermark; OpenAI adds SynthID and C2PA too. Leave watermarks in place.

### Keeping one style across hundreds of assets

1. **Style bible as references.** The approved exploration pick and reference sheets in `art/refs/` are attached to every call. No training needed; works with Nano Banana, GPT Image 2.5 and FLUX.
2. **Prompt template.** One fixed style paragraph from `docs/specs/art-direction.md`, plus the asset-specific line. Repeat the full description every call: models have no memory.
3. **Shared Blender rig.** Because the final assets are built in Blender with one palette, one lighting rig and one camera rig, style drift between reference sheets is largely ironed out at the build stage.
4. **LoRA training** once 15–50 approved assets exist: [fal FLUX.2 Klein trainer](https://fal.ai/models/fal-ai/flux-2-klein-9b-base-trainer) costs about $4 for 1,000 steps. The most reliable lock for large sets of shipped 2D images.
5. **Pose or shape control** with ControlNet or IP-Adapter, e.g. a pose or blockout rendered in Blender and fed back to the image model ([fal flux-general](https://modelgrep.com/media/models/fal-ai/flux-general), or ComfyUI locally). This also works in reverse of the main pipeline: a Blender greybox render as input for a painted reference.
6. **Post-process everything** onto `art/palette.json`, the same outline width and the same scale.

### Running locally

FLUX 3 Image Klein runs on an 8 GB GPU and is free for commercial use under $5M yearly revenue ([VentureBeat](https://venturebeat.com/technology/black-forest-labs-opens-flux-3-image-klein-weights-with-free-commercial-use-limited-to-smaller-businesses)); FLUX.2 Klein 4B is Apache 2.0. Qwen-Image-2.1 outputs native RGBA but is non-commercial. ComfyUI is the runner; Claude Code drives it through its HTTP API with JSON workflows. Licence summaries for the FLUX family conflict between sources: check the model card before shipping.

### What Claude itself is good for

Building from references: Blender geometry, SVG and HTML/CSS UI, icons, procedural tiles, effects and diagrams, all matched against an approved image. It is weak at inventing organic subjects and composition from words alone: benchmarks in 2026 still list faithful vector generation and spatial layout as unsolved ([Graphic-Design-Bench](https://arxiv.org/abs/2604.04192), [Willison](https://simonwillison.net/2026/Sep/22/opus-and-sol-and-luna/)). That weakness is exactly why the reference step comes first.

## Pixel art, sprites and animation

Pixel-art games follow the same reference-first rule: the look is designed with Nano Banana or GPT Image, then the actual sprites come from Blender rendered small and quantised (consistent, any number of directions) or from a dedicated pixel-art generator with the reference attached: Retro Diffusion for API control and tilesets, PixelLab for characters in 4 or 8 directions with animation. General models produce fake pixel art and always need cleanup.

**Why general models fail as final pixel art.** Diffusion models have no real pixel grid: blocks vary in size, sit off-grid, and the palette runs into tens of thousands of colours ([analysis](https://dev.to/jenissimo/how-to-tame-your-ai-pixel-art-3pk5)). Use them for design references, not shipped sprites. Never upscale pixel art with an AI upscaler; use nearest-neighbour.

| Tool | MCP | Price | Strengths |
| --- | --- | --- | --- |
| [Retro Diffusion](https://github.com/Retro-Diffusion/api-examples) | Official, `https://mcp.retrodiffusion.ai/mcp` | About $0.015–0.18 per image; animations $0.14–0.25; tilesets $0.10; free cost check | Seed, `input_palette`, `remove_bg`, seamless tiles, 8-direction rotation, walk/idle sheets, Wang tilesets |
| [PixelLab](https://github.com/pixellab-code/pixellab-mcp) | Official, `https://api.pixellab.ai/mcp` (subscription) | About $12/month (2,000 images) | `create_character` in 4 or 8 directions, `animate_character`, tilesets, isometric tiles; commercial use, no training on output |
| [Ludo](https://ludo.ai/blog/introducing-ludo-ai-api-mcp-integration) | Official HTTP MCP | $20–50/month | Sheets up to 64 frames; watermarked without a plan |
| [SpriteCook](https://spritecook.ai/agents) | Official MCP + Claude plugin | From $8/month | Animations, tilesets, UI kits |
| AutoSprite | API on paid plans | $12–29/month | Sheets from chosen moves |

**Cleanup.** Run every generated pixel asset through [`unfake`](https://pypi.org/project/unfake/) (MIT: grid detection, snap, quantise, `--palette`, `--transparent-background`) or Retro Diffusion's free Pixel Fixer, then check against `art/palette.json`.

### Animation routes

1. **Reference → Blender → sprites (default, most consistent):** build the model from the approved turnaround (Route A or B above), animate parts or the rig, then let a Claude-written Blender script render 8 directions with a transparent background and pack the sheet. Optionally pixelate with `unfake`. This is the route for robots, vehicles, units and buildings.
2. **2D generators:** PixelLab `animate_character`, Retro Diffusion animations (start frame 32–256 px), Ludo or SpriteCook, with the approved reference as input. Fast, but frames can drift.
3. **Image-to-3D for organic units:** Tripo or Meshy from the approved front view, auto-rig and retarget, then render through the same Blender rig as route 1.

## 3D generation

Image-to-3D is Route B of the default pipeline: its input is always an approved reference image, never a raw text prompt. Tripo is the default for game models that need rigging and animation; TRELLIS.2 is the free self-hosted option. Do not self-host Hunyuan3D open weights from the Netherlands: their licence excludes the EU.

| Service | Price | Topology control | Rigging | Output licence |
| --- | --- | --- | --- | --- |
| [Tripo](https://developers.tripo3d.ai/en/pricing) | $0.30 image-to-3D with texture; +$0.10 smart low-poly; $0.25 auto-rig; $0.10 per retarget | Quad output, face limit | Yes | Paid plans commercial and private; free plan non-commercial |
| [Meshy](https://docs.meshy.ai/en/api/pricing) 7.1 | 30 credits textured; remesh 5; rig 5; animation 3 per action | Remesh to target polycount | Yes | Pro and up: you own it; free plan CC BY 4.0 |
| [Rodin Gen-2](https://runware.ai/docs/models/hyper3d-rodin-gen-2) | $0.40 per model | `polyCount` 500–1M, quad or tris, PBR | No | Check terms |
| Hunyuan3D v3.1 (API via fal) | $0.225–0.375 | — | No | API fine; open 2.x weights exclude EU, UK, South Korea ([analysis](https://www.contrast3d.com/blog/hunyuan3d-licencia-union-europea/)) |
| [TRELLIS.2](https://huggingface.co/microsoft/TRELLIS.2-4B/blob/main/README.md) (local) | Free | GLB with PBR | No | MIT; needs 24 GB VRAM on Linux |

All of these are also available through NanoGPT, at roughly $0.10–1.44 per model.

**Pipeline.** Approved reference (front view or turnaround from `art/refs/`) → image-to-3D → remesh to the polygon budget → auto-rig → Blender script imports the GLB, applies the project lighting rig and palette materials, compares a render against the reference (step 6 above), and renders previews or sprites. Claude drives Blender headless (`blender -b -P script.py`); an MCP server is optional. The community [Blender MCP](https://www.strayspark.studio/blog/official-blender-mcp-server-comparison-2026) runs arbitrary Python, so only use it in a sandbox.

## Sound effects

Keep code synthesis (ZzFX/jsfxr, numpy) for retro and UI sounds, and use the ElevenLabs Sound Effects API for realistic foley, impacts and ambience. Most open sound models cannot be used in a commercial game.

| Option | Access | Length and looping | Price | Commercial use |
| --- | --- | --- | --- | --- |
| ZzFX / jsfxr / numpy (current stack) | Code in the repo | Any; deterministic | Free | Yes; no AI disclosure needed |
| [ElevenLabs Sound Effects v2](https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert.md) | REST `POST /v1/sound-generation`, `loop` flag, `duration_seconds`, `prompt_influence` | 0.5–30 s; seamless-loop mode | $0.12 per minute via API ([pricing](https://elevenlabs.io/pricing/api)); about $0.01 per clip via NanoGPT | Paid plans yes, except beta services; free plan no |
| [Stable Audio 2.5](https://www.therundown.ai/tools/stable-audio-2-5) / [3.0](https://www.therundown.ai/tools/stable-audio-3-0) API | Stability platform | Up to 3 min / 6 min, inpainting | $0.20 / $0.26 per generation | Rights assigned to you |
| [Stable Audio Open Small](https://huggingface.co/stabilityai/stable-audio-open-small) (local) | Hugging Face weights | Up to 11 s | Free | Only under $1M yearly revenue, registration required |
| MMAudio, AudioGen, Sony Woosh (local) | Open weights | About 8–10 s | Free | No: CC-BY-NC |

**Free libraries.** The [Sonniss GDC 2026 bundle](https://rekkerd.org/sonniss-releases-gdc-2026-game-audio-bundle/) (7.47 GB) is royalty-free for sold games but may not be used for AI training. Kenney audio packs are CC0. Freesound is licensed per file: CC0 and CC-BY are usable, CC-BY-NC is not.

**Workflow.** Generate 3–5 variants per event, normalise, render a spectrogram, and let the human pick. Name files after sim events (`unit_died.ogg`) as in GAME-STACK.md. ElevenLabs credit costs are described inconsistently across its own pages, so check the cost of the first calls.

## Music and adaptive music

Make hero tracks by hand in Suno (Premier, for stems), and use an API music model only for variations, stingers and placeholders. Suno has no official API; agent-driven music goes through ElevenLabs Music, Lyria, Stable Audio or local ACE-Step.

| Service | API | Length | Stems | Price | Game licence |
| --- | --- | --- | --- | --- | --- |
| Suno v6 (live since 9 September 2026) | No; only "exploring" one with partners | Up to 8 min | Up to 12 in Studio (Premier) | Pro $10/mo, Premier $30/mo | Commercial only for songs downloaded on a paid plan through Suno's own channels ([terms](https://suno.com/terms)) |
| [ElevenLabs Music](https://elevenlabs.io/docs/overview/capabilities/music) v2.5 | Yes, paid plans | 3 s to 5 min | 2–6 depending on plan | $0.15 per minute | Self-serve plans allow indie games: game revenue under $500k and developer under $1M per year ([music terms](https://elevenlabs.io/music-terms)) |
| [Google Lyria 3 / 3.5](https://ai.google.dev/gemini-api/docs/music-generation) | Yes, Gemini API (preview) | Clip 30 s; 3.5 a few minutes | No | About $0.04–0.08 per song (secondary sources) | SynthID watermark; indemnity unconfirmed |
| [Lyria RealTime](https://ai.google.dev/gemini-api/docs/realtime-music-generation) | Yes, experimental WebSocket | Streaming | Mute bass or drums live | Not published | Instrumental only |
| Stable Audio 2.5 / 3.0 | Yes | 3 min / over 6 min | No | $0.20 / $0.26 per generation | Rights assigned to you |
| [ACE-Step 1.5](https://blog.comfy.org/p/ace-step-15-xl-commercial-grade-music) (local) | ComfyUI / Python | 10 s to 10 min | Not confirmed | Free on your own GPU | MIT |
| Udio | No | — | — | — | Downloads disabled since 29 October 2025: unusable |
| Meta MusicGen | Local | — | — | Free | CC-BY-NC: unusable |

**Suno wrappers.** Unofficial "Suno APIs" scrape or automate the website. Suno's terms forbid that, and material obtained that way arguably falls outside the commercial clause. Download manually, then hand the WAVs and stems to Claude Code. Write Suno prompts in English.

### Adaptive music

- Get stems from Suno Studio, ElevenLabs Music, or Demucs separation of a finished mix.
- Find loop points with [pymusiclooper](https://pypi.org/project/pymusiclooper/) (MIT): `export-points`, `split-audio` into intro/loop/outro, `tag` for `LOOP_START`/`LOOP_END`.
- In a browser game, start all stems on one AudioContext clock and crossfade gain nodes by game intensity. FMOD or Wwise (both free for small indies) only pay off for native or Steam builds.
- Write the music brief as data in `audio/music/*.json`: tempo, key, mood, instruments, intensity layers, loop length. Claude turns it into prompts for each model.

## Voice and dialogue

Use ElevenLabs direct for shipped voices (best quality, Dutch supported, commercial on paid plans), and Kokoro or Chatterbox locally for free placeholders. Never clone a real person's voice without written consent.

| Option | Strengths | Price | Licence |
| --- | --- | --- | --- |
| [ElevenLabs TTS](https://elevenlabs.io/docs/overview/capabilities/text-to-speech) | v4 (90+ languages, multi-speaker dialogue), Multilingual v2 (incl. Dutch), Flash v2.5 (~75 ms); Voice Design from a text description | $0.04–0.08 per 1K characters; about 2× via NanoGPT | Paid plans commercial; free plan non-commercial |
| [OpenAI TTS](https://developers.openai.com/api/docs/guides/text-to-speech) (`gpt-4o-mini-tts`) | Steerable tone and accent; 13 voices; English-optimised | Token-billed, cheap | Policy requires telling players the voice is AI-generated |
| Kokoro-82M (local) | Fast, small | Free | Apache 2.0; no cloning, no Dutch |
| Chatterbox (local) | 23 languages, cloning | Free | MIT |
| F5-TTS, XTTS-v2 | Good quality | Free | Non-commercial: unusable |

**Ethics and rules.**

- The SAG-AFTRA Interactive Media Agreement (to October 2028) binds only signatory studios, but its rules are a good baseline: written consent per use for any replica, no "sounds like [actor]" prompts.
- The EU AI Act Article 50 applies from 2 August 2026. Generic fictional NPC voices are probably outside the deepfake rules; a conversational AI NPC may require telling players they talk to an AI.
- Many indies use grunts, short barks or partial voice-over instead of full dialogue. It is cheaper to change late.

## NanoGPT

NanoGPT is the best single gateway for prototyping and most image, 3D and video work: one key and one MCP server cover nearly every asset type at close to direct prices. For the reference-first pipeline it is one of three equal routes (with Gemini direct and OpenAI direct); check its catalogue for the newest Nano Banana version before choosing it. Go direct for shipped music, voice, transcription, bulk FLUX and pixel art. The full API reference is `NANOGPT-API.md`.

**What it is.** A prepaid pay-as-you-go aggregator run by NanoGPT LLC (California law), grown out of the Nano crypto community and running since at least January 2024. Deposits by card from $1 or crypto; text models at provider list price, with a 5% fee for pinned providers or BYOK.

**The subscription is not for game assets.** The $12/month Pro plan (60M open-model input tokens per week, 100 images per day) is for personal, non-commercial use only. Pay commercial assets from the pay-as-you-go balance.

### What it offers for games

| Category | Useful models | Gap |
| --- | --- | --- |
| Image | GPT Image 2 / 2.5, Nano Banana 2 / Pro, Seedream 5, FLUX.2, Recraft V4.1 (vector), Ideogram V3 Transparent, Qwen Image | No pixel-art or sprite model; Nano Banana 2.1 availability to be checked; avoid the Midjourney route (no official API) |
| Image utilities | BiRefNet V2 background removal ($0.01), SAM 3 segmentation, upscalers, depth maps | — |
| 3D | Meshy 6–7.1, Tripo 2.5 / P2, TRELLIS.2, Hunyuan3D V3, Rodin 2.5 ($0.10–1.44 per model) | — |
| Sound effects | ElevenLabs Sound Effects V2 (about $0.01 per generation) | — |
| Music | ElevenLabs Music v2.5, Lyria 3, MiniMax Music, Stable Audio 3, ACE-Step 1.5; Demucs stem separation | No Suno; API documents only a text `input`, no lyrics, duration or stems |
| Voice | ElevenLabs v3/v4, OpenAI TTS, Gemini TTS, Kokoro, Qwen TTS with cloning | About 2× ElevenLabs direct |
| Video | Veo 3.1, Kling, Seedance, Wan, Hailuo (trailers, animated key art) | — |

### Price check against going direct

| Model | NanoGPT | Direct | Verdict |
| --- | --- | --- | --- |
| Nano Banana Pro, 1K/2K | $0.14 | $0.134 | About equal |
| GPT Image 2.5 Flare, 1K high | $0.153 | about $0.21 (token-billed) | NanoGPT cheaper at high quality |
| FLUX.2 pro, 1 MP | about $0.051 | $0.03 | Go direct for bulk |
| Veo 3.1 Fast, 8 s 720p | $0.64 | about $0.80 | NanoGPT cheaper |
| ElevenLabs v3 TTS, per 1K chars | about $0.17 | $0.08 | Go direct |
| ElevenLabs Scribe STT, per hour | about $3.06 | $0.22 | Go direct |

Listed media prices can assume default quality: GPT Image 2 at `quality: high` was billed about 2.4× the listed price. Always log the `cost` field of the first real call.

### Rights, privacy and reliability

- You own the output and may use it commercially, but each model's provider terms still apply on top. For ElevenLabs music bought through NanoGPT it is unclear which ElevenLabs licence tier applies; buy shipped music direct.
- Prompts and outputs are not logged or used for training by default; upstream providers keep their own retention.
- Trustpilot scores 3.7/5 from 10 reviews; subscription terms changed several times in 2026; no public status page was found.
- Image API: no streaming, no provider choice, seed is a hint only, parameters differ per model.

### How Claude Code uses it

- Add the MCP server at user scope: `claude mcp add nanogpt --scope user --env NANOGPT_API_KEY=… -- npx -y @nanogpt/mcp`.
- Give each game its own key with a USD-per-day cap.
- Video and 3D jobs are charged on submit: poll the `runId`, never resubmit.

## Aggregators, MCP servers and CLIs

Register two or three MCP servers at user scope and call everything else with small scripts: NanoGPT as the broad gateway, plus Retro Diffusion or PixelLab for pixel art, plus ElevenLabs direct for shipped audio. Gemini and OpenAI image calls go through `tools/gen_image.py` with `GEMINI_API_KEY` or `OPENAI_API_KEY`.

### Aggregators

| Service | Coverage | Fees | Use it for |
| --- | --- | --- | --- |
| NanoGPT | Text, image, video, audio, music, 3D in one balance | Text at list price; media priced per model | Default gateway, prototyping, 3D |
| [fal.ai](https://fal.ai/docs/documentation/model-apis/mcp) | 1,000+ image, video, audio, 3D models; LoRA training; richest parameters | Per unit | LoRA training, ControlNet/IP-Adapter, FLUX at direct price |
| [Replicate](https://replicate.com/blog/remote-mcp-server) | Huge open-model catalogue | Per GPU second or output | Custom or fine-tuned models |
| OpenRouter | Text-first, few media models | 5.5% on credit purchases | Text only |

### MCP servers worth adding

| Server | Type | Endpoint or install |
| --- | --- | --- |
| NanoGPT | Official | `npx -y @nanogpt/mcp` (stdio, `NANOGPT_API_KEY`) |
| fal | Official | `https://mcp.fal.ai/mcp-relay` (OAuth) |
| Retro Diffusion | Official | `https://mcp.retrodiffusion.ai/mcp` |
| PixelLab | Official | `https://api.pixellab.ai/mcp` |
| ElevenLabs | Official, hosted | `https://api.elevenlabs.io/v1/mcp` (OAuth); the local server is archived |
| Tripo | Vendor | `VAST-AI-Research/tripo-mcp` |
| Blender | Official (Blender Lab) and community | Optional, for interactive exploration of a reference build; headless recipe scripts stay the source of truth |

**MCP or script?** Use MCP for exploration in a conversation. For anything repeatable, put the call in `tools/gen_*.py` with the recipe in the repo: it is reproducible, testable and cheaper on context. Keep every API key in an environment variable, never in a committed file, and give each game its own key with a daily spending cap.

## Post-processing and verification

Every generated file passes through a scripted pipeline before it reaches `art/refs/` or `public/assets/`, and Claude must read its preview before reporting done. The human approves reference sets and hero assets.

### Images

1. Generate n variants with the recipe (prompt, model, references, seed where supported).
2. Reference sheets: slice views, crop, normalise height, extract the palette (k-means), store in `art/refs/`.
3. Shipped images: remove the background with native transparency (GPT Image 2.5) or BiRefNet (Apache, about $0.01 via NanoGPT). BRIA RMBG-2.0 open weights are non-commercial.
4. Pixel art: `unfake` to the project palette; never AI-upscale. HD art: upscale only when needed (Recraft Crisp $0.004, SeedVR2 $0.0025 per MP).
5. Normalise scale, pivot, outline and palette with Pillow.
6. Write a contact sheet or reference-vs-render comparison to `build/previews/` and an in-game screenshot via Playwright. Claude reads both.
7. Pack atlases and update `assets/manifest.json`.

### Audio

1. Generate WAV (or Opus) variants.
2. Measure loudness: `ffmpeg -i in.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null -`.
3. Trim silence (`silenceremove`) and make loops (`pymusiclooper`, or `acrossfade`).
4. Normalise with the second loudnorm pass in linear mode.
5. Encode to OGG/Opus with an MP3 fallback.
6. Render waveform and spectrogram PNGs (`showwavespic`, `showspectrumpic`) and store the loudness JSON.
7. The human listens and approves.

Loudness targets: PlayStation guidance is -24 LUFS ±2 for console and -18 LUFS ±2 for portable, max -1 dBTP. There is no PC standard; about -16 to -18 LUFS for the overall browser or PC mix is reasonable. Normalise each category (music, SFX, voice) consistently and balance them in the in-game mixer.

### The asset manifest

One entry per shipped file and one per approved reference: path, recipe or build-script hash, provider, model id, date, prompt hash, cost, plan or licence, the references a shipped asset was built from, whether AI pixels were projected or shipped directly, and whether a human edited it. This single file answers the Steam AI disclosure, licence questions and Content ID disputes.

## Legal, licensing and Steam AI disclosure

Shipped AI art and audio must be disclosed on Steam, purely AI-generated assets are probably not protected by copyright, and the licence of each model decides whether you may sell the game at all. This is general information, not legal advice.

**Steam.** Since the 16–17 January 2026 form, any pre-generated AI content that ships with the game and is consumed by players (art, sound, music, text, voice, store-page material) must be described on the store page. Live-generated content must also describe its guardrails. AI coding tools such as Claude Code are exempt ([Steamworks](https://partner.steamgames.com/doc/gettingstarted/contentsurvey)). A June 2026 per-asset tagging rule is reported by one secondary source only and is unconfirmed.

**Reference-first and disclosure.** When assets are built in Blender from AI reference images, the AI images themselves do not ship, but the designs players see came from them. Treat this conservatively: disclose that AI image generation was used for concept and reference art, and disclose more specifically where AI pixels are projected into textures or shipped directly (UI elements, portraits, key art). The manifest records exactly which is which, so the disclosure text can be accurate.

**Copyright.** The US Supreme Court declined *Thaler v. Perlmutter* on 2 March 2026: a human author is required. Human selection, arrangement and editing can be protected; EU law likewise requires the author's own intellectual creation. Raw AI sprites and tracks can probably be copied by others. Rebuilding a design in Blender under human direction, with human selection at every step, strengthens the authorship story compared with shipping raw images, but it does not guarantee protection. Keep prompt logs, selection notes and records of your edits.

**EU AI Act Article 50** (from 2 August 2026): providers must mark synthetic output machine-readably; deployers have a lighter duty for evidently fictional works. Do not strip SynthID or C2PA marks from shipped AI images.

### Licence traps

| Trap | Rule |
| --- | --- |
| Free plans | ElevenLabs, Tripo, Meshy, Suno free plans are non-commercial or need attribution. Generate shipped assets on a paid plan |
| NanoGPT subscription | Personal, non-commercial only; pay shipped assets and references from the balance |
| Gemini free tier / AI Studio app | Use an API key on a billed project for game work; check the Gemini API terms for commercial use of outputs |
| Non-commercial weights | MMAudio, AudioGen, MusicGen, F5-TTS, XTTS, Qwen-Image-2.1, BRIA RMBG-2.0 |
| Revenue caps | Stable Audio Open (under $1M), FLUX 3 Klein (under $5M), ElevenLabs Music self-serve (game under $500k) |
| Region | Hunyuan3D open weights exclude the EU |
| Unofficial APIs | Midjourney and Suno wrappers break the provider's terms |
| Training bans | Sonniss bundle and PixelLab output may not be used to train models |
| Look-alikes | Never prompt references "in the style of" a living artist or "like <existing game unit>"; describe the look in your own words |

**YouTube Content ID.** Never register your own AI game music with Content ID, opt out at the distributor if you release the soundtrack, and consider a streamer-safe music toggle.

## Decision checklist for a new game

Answer these in `docs/specs/000-stack.md` before generating the first asset; most are decided once per game.

1. **Art style.** Pixel art, flat vector, painted 2D, low-poly 3D or pre-rendered 3D sprites? This picks the build route (A, B, C or direct) after the reference step.
2. **Reference route.** Gemini direct, OpenAI direct or NanoGPT; which key, with which daily cap. Nano Banana 2.1 or GPT Image 2.5 as the main reference model.
3. **Asset groups.** Which groups get their own exploration and reference round (units, buildings, characters, UI, icons, environment).
4. **Asset volume.** Under 50 hero assets: references plus manual selection. Hundreds: train a LoRA once the style bible exists, or lean on parametric Blender recipes.
5. **Gateway and direct accounts.** NanoGPT key, plus which direct accounts (Gemini, OpenAI, ElevenLabs, Retro Diffusion or PixelLab, Suno Premier).
6. **Budget.** A monthly ceiling for generation, checked against the `cost` log.
7. **Audio direction.** Code-synthesised retro, generated realistic, or a mix; music by hand in Suno or via API; voice yes or no.
8. **Licences.** Every chosen model allowed for commercial use at the expected revenue; no free plans for shipped assets.
9. **Disclosure.** Manifest in place from day one, including references, so the Steam AI text writes itself.
10. **Review.** Who approves what: Claude checks previews, comparisons and loudness; the human picks reference sets and approves every hero asset and every track.

## Key sources

- [Gemini Nano Banana 2.1 model page](https://ai.google.dev/gemini-api/docs/models/gemini-nano-banana-2.1) · [Gemini image generation](https://ai.google.dev/gemini-api/docs/image-generation) · [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [OpenAI API pricing](https://developers.openai.com/api/docs/pricing) · [BFL pricing](https://bfl.ai/pricing)
- [NanoGPT pricing](https://nano-gpt.com/pricing) · [NanoGPT terms](https://nano-gpt.com/legal/terms-of-service) · [NanoGPT docs](https://docs.nano-gpt.com)
- [ElevenLabs API pricing](https://elevenlabs.io/pricing/api) · [ElevenLabs music terms](https://elevenlabs.io/music-terms) · [Suno terms](https://suno.com/terms)
- [Retro Diffusion API](https://github.com/Retro-Diffusion/api-examples) · [PixelLab MCP](https://github.com/pixellab-code/pixellab-mcp) · [Tripo pricing](https://developers.tripo3d.ai/en/pricing) · [Meshy pricing](https://docs.meshy.ai/en/api/pricing)
- [Steam content survey](https://partner.steamgames.com/doc/gettingstarted/contentsurvey) · [EU AI Act Art. 50](https://artificialintelligenceact.eu/transparency-rules-article-50/)
