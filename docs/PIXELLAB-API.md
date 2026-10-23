# PixelLab API — a complete working reference

> **Master copy:** the GitHub repo `jackdamnielzz/gamedev-kit`, folder `docs/`. Copies elsewhere follow the repo; change the repo first.

A portable guide for an AI agent or developer who uses PixelLab as the art generator of a game: what the service is, which models and endpoints exist, every setting that matters per endpoint, sizes, costs, limits, licence, errors, and how it fits the kit's reference-first pipeline.

Sources: the OpenAPI spec at https://api.pixellab.ai/v2/openapi.json (102 paths, the source of truth for every parameter), https://api.pixellab.ai/v2/llms.txt, https://www.pixellab.ai/llms-full.txt, the terms of service, and free API calls made on **23 October 2026** (`/balance`, `/pro-flash/capabilities`, `/pro-flash/cost`). Endpoints, sizes and prices change often: check the spec and the cost endpoints before relying on a number in this file.

---

## 1. What PixelLab is

PixelLab (Sweden; governed by Swedish law) makes game-ready **pixel art** with its own models trained for the pixel domain: images, characters with 4 or 8 directions, animations, tilesets, isometric tiles, map objects, UI panels, pixel fonts, portraits with lip-sync, VFX, and cleanup tools (unzoom, colour reduction, background removal, normal maps). Access routes:

| Route | Use it for |
| --- | --- |
| REST API `https://api.pixellab.ai/v2` | Scripts in the repo (`tools/gen_image.py`, recipes); reproducible runs |
| MCP server `https://api.pixellab.ai/mcp` (same token) | Exploration inside a Claude Code conversation; the `pixelart_workbench` and `vfx_workbench` tools let the agent edit pixels itself, free for subscribers |
| SDKs | Python `pip install pixellab` (github.com/pixellab-code/pixellab-python), JS/TS (github.com/pixellab-code/pixellab-js) |
| Web editor, Aseprite and Pixelorama plugins | Hand touch-up by the human |

The v1 API (`https://api.pixellab.ai/v1`) still exists but is legacy; use v2. "Programmatic usage is only allowed through our official API" (terms 2.2).

## 2. Authentication and key safety

- `Authorization: Bearer <token>` on every request. Token from https://pixellab.ai/account. The same token works for the MCP server.
- Keep it in the user environment variable **`PIXELLAB_API_KEY`**; never print, log or commit it. On Windows: `[Environment]::SetEnvironmentVariable('PIXELLAB_API_KEY', '<token>', 'User')`, then restart the editor.
- Without a token, endpoints answer `401`.

## 3. Plans, money and licence

**Billing unit:** subscription **generations** (most endpoints), or USD **credits** (pay-as-you-go top-up). Every response carries `usage` (`{"type": "generations", "generations": n}` or `{"type": "usd", "usd": x}`); log it.

| Plan (October 2026, secondary sources; check the site) | Price | Generations / month | Notes |
| --- | --- | --- | --- |
| Free trial | €0 | about 40 fast, then about 5 per day (store up to 20) | No credit card; some tools locked |
| Tier 1 "Pixel Apprentice" | about $12 / month | **2,000** (confirmed by `/balance`) | Most Pro tools, animation, vocal animation |
| Tier 2 "Pixel Artisan" | about $24 / month | about 3,000 (unconfirmed) | Priority queue, larger canvases (400×400), experimental tools |
| Tier 3 "Pixel Architect" | about $50 / month | 6,000–10,000 (sources disagree) | Top priority, up to 20 concurrent jobs, team features |

- When subscription generations run out, a small **daily bonus** (+5 per night, up to 20) is used, then credits.
- Some canvas limits depend on the tier (for example pixflux and inpainting: free 200×200 area, Tier 1 320×320, Tier 2+ 400×400). Endpoints refuse oversize requests before charging.

**Licence (terms of service):**

- "You retain ownership of any content you create using PixelLab", for "both commercial and non-commercial purposes", on **all** plans.
- **You may not train models on the output** unless PixelLab permits it in writing. Record this in the asset manifest licence field.
- Building a competing or reselling service on the API needs PixelLab's permission.
- PixelLab says it does not use inputs or outputs for training, and does not store generated images unless a tool says so (characters, objects, tilesets and UI assets are stored in your library on purpose).
- Shipped PixelLab sprites are AI pixels: `ai_pixels_shipped: true` in the manifest and part of the Steam AI disclosure.

## 4. How requests work

- **Image object:** every image in a request or response is `{"type": "base64", "base64": "<data>", "format": "png"}`. Sizes are `{"width": w, "height": h}`.
- **Synchronous endpoints** (pixen, pixflux, bitforge, rotate, inpaint, resize, remove-background, unzoom, reduce-colors, correct-pixelart, image-to-pixelart, estimate-skeleton, image-to-text, talking-gif, lip-sync) return the image in the response: `{"image": {...}, "usage": {...}}`.
- **Background jobs** (all Pro, Pro Flash, v3 and most creation endpoints) return `202` or `200` with `background_job_id` (and often `character_id`, `object_id`, `tileset_id`, `ui_asset_id`) at once. Poll `GET /v2/background-jobs/{id}` every 5–10 s until `status` is `completed` or `failed`; results are in `last_response` (images under `last_response.images`, Pro Flash also `image_url` and `source_image_id`). While waiting, `last_response.queue_position` and `estimated_wait_seconds` show the GPU queue; a waiting job is not stuck.
- **Resource endpoints** answer `423 Locked` with a `Retry-After` header while still generating (`/tilesets/{id}`, `/map-objects/{id}`, `/characters/{id}/zip` …).
- **Cancel:** `DELETE /v2/background-jobs/{id}` frees the concurrency slot; a queued job is not charged, a running one may still be.
- **Uploads:** `POST /v2/uploads` (multipart `file`) stores an image for 3 days for free and returns a reference other tools accept; MCP clients get an upload URL from `get_upload_url`.
- **Stored assets:** characters, objects, tilesets, tiles, UI assets live in your library (`GET /characters`, `/objects`, `/tilesets`, `/ui-assets`, list endpoints with `limit`/`offset` up to 100). **Map objects are deleted 8 hours after creation**: download them at once.
- **Seeds:** most endpoints take `seed` (0 or omitted = random). Pro Flash records the seed but does not promise determinism. Treat AI output as non-deterministic: generate once, approve, commit.

## 5. Choosing a model

| Model family | Endpoints | Character | Typical cost |
| --- | --- | --- | --- |
| **Pixen** | `/create-image-pixen`, `/edit-image-pixen` | Fast default text-to-image, clean small sprites, 16 to 512×512 area, sides multiple of 4; outline/detail/view/direction controls | 1 generation (+0.05 with `enhance_prompt`) |
| **Pro** (stronger, slower) | `/generate-image-v2`, `/generate-with-style-v2`, `/edit-images-v2`, `/inpaint-v3`, `/interpolation-v2`, `/edit-animation-v2`, `/transfer-outfit-v2`, `/generate-8-rotations-v2`, `/generate-ui-v2`, `/create-character-pro`, objects, UI panels, fonts | Highest quality; small sizes return a **grid of many candidates in one call** (up to 64 at ≤32 px) | About 10–25 generations per call |
| **Pro Flash** (new) | `/create-image-pro-flash`, `/edit-image-pro-flash`, `/inpaint-image-pro-flash`, `/create-character-pro-flash`, `/create-object-pro-flash`, `/image-to-pixelart-pro-flash` | One high-quality native pixel image per call, optional style image; reusable `source_image_id` for later rotations | Measured 23 Oct 2026: 5 (≤64×64), 6 (128×128), 9 (256×256); character 64×64 8 directions = 6, 96×96 = 7. Ask `GET /pro-flash/cost` first |
| **v3** | `/create-character-v3`, `/animate-with-text-v3`, `/generate-8-rotations-v3`, character animation `mode: "v3"` | Rotation and animation from a south-facing sprite; best price/quality for characters | Rotation `ceil(w·h·8/65536)`; animation `ceil(w·h·frames/65536)` per direction (64 px, 8 frames = 1) |
| **PixMiniMax** (beta, MiniMax H3) | `/animate-pixminimax`, animation `mode: "pixminimax"` | Long clips (4–40 frames, multiples of 4) at any size up to 256 | 64×64: 4/8/16/40 frames = 1/1/2/6 per direction |
| **Pixflux** | `/create-image-pixflux` (+ `-background` job variant) | Older general model, large canvases (32×32 to 400×400 area), init image, forced palette | Low |
| **Bitforge** | `/create-image-bitforge` | Older small/medium model (≤200×200 area) with style image, inpainting, skeleton guidance | Low |
| Template / skeleton | `/create-character-with-4-directions`, `-8-directions`, `/animate-character`, `/animate-with-skeleton(-v3)` | Classic mannequin-template characters and template animations | 1 per direction for templates |

Rules of thumb: **pixen** for quick single sprites; **Pro** when you want a sheet of many candidates to choose from in one call; **Pro Flash** for one best image or a reusable south frame; **v3** to rotate and animate characters; **PixMiniMax** for longer motion. Legacy endpoints (`/animate-with-text`, `/animate-with-text-v2`, `/inpaint`, `/edit-image`, `/rotate`, bitforge, pixflux, template characters) still work and are not scheduled for removal, but new integrations should start with the newer ones.

## 6. Shared options (apply wherever the endpoint lists them)

| Option | Values | Notes |
| --- | --- | --- |
| `view` | `side`, `low top-down` (~20° from horizontal, classic 3/4 RPG), `high top-down` (~35°); some endpoints add `perspective`, `oblique`, `none` | Weak guidance on older models; required context on v3/PixMiniMax |
| `direction` | `south` (facing the camera), `south-east`, `east` (facing right), `north-east`, `north` (back), `north-west`, `west`, `south-west`; some add `none` | v3 rotation input **must face south (straight at the viewer)**, otherwise all 8 labels shift by 45° |
| `outline` | `single color black outline`, `single color outline`, `selective outline`, `lineless` | Soft guidance |
| `shading` | `flat shading`, `basic shading`, `medium shading`, `detailed shading`, `highly detailed shading` | Soft guidance; roughly "how many colours per material" |
| `detail` | `low detail`, `medium detail`, `highly detailed` (some endpoints: `high detail`) | Soft guidance |
| `isometric`, `oblique_projection` | booleans | Older models; tiles have their own controls |
| `no_background` | boolean | Transparent output; pixen only up to 65,536 px area; `background_removal_task`: `remove_simple_background` (fast) or `remove_complex_background` |
| `text_guidance_scale` | 1–20, default 8 | How literally to follow the text; too high gives over-saturation |
| `init_image` + `init_image_strength` | 1–999, default 300 | 0–300 rough colour hint · 300–400 rough shapes and colours · 400–600 variations · 600–900 small edits to a nearly finished piece |
| `color_image` (+ `force_colors`) | image whose colours form the palette | Older palette mechanism |
| **`target_palette`** (beta, on newer endpoints) | `{"colors": ["#081820", …], "name": "Game Boy", "max_colors": 2–64, "smart": false}` | Every output pixel is one of `colors`; `max_colors` caps per image; `smart` (single images) maps whole objects (skin stays skin) at +15–60 s. **Use the project palette from `art/palette.json` (as hex) here.** With a style image, set `style_options.color_palette: false` |
| `style_image` + `style_options` | `{"color_palette", "outline", "detail", "shading"}` booleans, default all true | What to copy from the style image |
| `seed` | integer ≥ 0 | 0 = random |
| `enhance_prompt` | boolean | Let PixelLab expand the description first (+0.05 generations); the expanded text comes back in `enhanced_prompt` |
| `proportions` (template characters) | preset `default`, `chibi`, `cartoon`, `stylized`, `realistic_male`, `realistic_female`, `heroic`, or custom `head_size`, `arms_length`, `legs_length`, `shoulder_width`, `hip_width` (0.5–2.0) | Ignored by Pro and v3 |
| `template_id` | `mannequin` (the only humanoid), `bear`, `cat`, `dog`, `horse`, `lion` | Skeleton for animation; not "humanoid" |

**Before any reference image goes in:** run upscaled pixel art through `POST /unzoom` (min 256×256, max 2048×2048 area; output is opaque on white, so remove the background again). PixelLab names upscaled references "the most common cause of disappointing output".

## 7. Endpoint reference

Only the settings that matter are listed; `seed`, `no_background` and `target_palette` exist on almost all newer endpoints and are left out of the tables. `*` = required.

### 7.1 Images

| Endpoint | Key settings | Sizes and output |
| --- | --- | --- |
| `POST /create-image-pixen` (sync) | `description*`, `image_size*`, `outline`, `detail` (default highly detailed), `view`, `direction`, `enhance_prompt` | Min side 16, max area 512×512, sides multiple of 4, square below 32; 1 image |
| `POST /generate-image-v2` (Pro, job) | `description*` (≤2000), `image_size*`, `reference_images` (≤4, subject guidance), `style_image` + `style_options` | 16 to 512×512 square (688×384 at 16:9). **Candidates per call by max side:** ≤32 → 64, 33–35 → 49, 36–41 → 36, 42–50 → 25, 51–64 → 16, 65–84 → 9, 85 → 16, 86–170 → 4, >170 → 1 |
| `POST /generate-with-style-v2` (Pro, job) | `style_images*` (1–4), `description*`, `style_description` | Output size = largest style image (16–512, square); same candidate counts |
| `POST /create-image-pro-flash` (job) | `description*`, `image_size*`, `style_image` (`{image, size, usage_description}`), `style_options` | Native presets 24, 32, 32×48, 48, 64, 96×64, 96, 128 (16 experimental); custom 16–256 in steps of 4 (beta); 1 image + `source_image_id` |
| `POST /create-image-pixflux` (sync) / `-background` (job) | `description*`, `image_size*`, `text_guidance_scale`, outline/shading/detail/view/direction, `isometric`, `init_image(_strength)`, `color_image` | 32×32 to 400×400 area (tier limits) |
| `POST /create-image-bitforge` (sync) | as pixflux + `style_image`, `style_strength` 0–100, `inpainting_image` + `mask_image`, `skeleton_keypoints`, `coverage_percentage`, `negative_description` | ≤200×200 area |
| `POST /image-to-pixelart` (sync) | `image*`, `image_size*`, `output_size*` (about ¼ of input), `fixer` (faithful mode), `init_image_strength` (100–300 useful) | In 16–2048, out 16–512 |
| `POST /image-to-pixelart-pro` / `-pro-flash` (job) | `image*`, optional `description` | Output size chosen automatically; Pro Flash 6 generations |

### 7.2 Characters

| Endpoint | Key settings | Notes |
| --- | --- | --- |
| **`POST /create-character-v3`** (job; most used) | `description*`; `reference_image` (south-facing, ≤256) **or** from scratch with `image_size` (32–256, default 64); `n_directions` 4/8 (reference mode); `direction_images` (your own drawings for other directions, used as drawn; all covered = import for 0.25); `view`; `template_id`; `outline`/`detail` (scratch mode); `enhance_prompt` | Cost: reference `ceil(w·h·8/65536)`; scratch 1 + that. Stored as a character that can be animated, listed and exported |
| `POST /create-character-pro` (job) | `description*`, `image_size*` (32–168), `method` (`create_with_style`, `create_from_concept`, `rotate_character`), `concept_image` (≤1024), `reference_image` (≤168), **`style_character_id`** (match an existing 8-direction character), `style_description`, `view`, `template_id` | 10–25 generations; best for a consistent cast |
| `POST /create-character-pro-flash` (job) | `description*`, `image_size`, `style_image`, `source_image_id` or `first_frame` (reuse a chosen south frame and pay only rotations), `n_directions`, `view`, `template_id` | 64×64 8 directions = 6 generations |
| `POST /create-character-state` (job) | `character_id*`, `edit_description*`, `override_frame_size` (room for a weapon, wings), `use_color_palette_from_reference` | Same edit on all directions, saved as a grouped "state" (outfit, injury, costume) |
| `POST /create-character-with-4-directions` / `-8-directions` (job) | template-based: `proportions`, `outline`, `shading`, `detail`, `view` (`side`, `low top-down`, `high top-down`, `perspective`), `color_image`, `directions` (frozen own sprites), `mode` `standard` (1) or `pro` (10–25) | Legacy-style but cheap |
| Library | `GET /characters`, `GET /characters/{id}` (rotation URLs), `GET /characters/{id}/zip` (rotations, animation frames, `metadata.json` with keypoints), **`GET /characters/{id}/spritesheet`** (one uniform-grid PNG + layout JSON: row 0 rotations, then one row per animation-direction; pivot = cell centre), `PATCH …/tags`, `DELETE …` | Export endpoints need no auth: the random id is the key |

### 7.3 Animation

| Endpoint | Key settings | Limits and cost |
| --- | --- | --- |
| **`POST /characters/animations`** (`/animate-character` is the same) | `character_id*`; `mode`: **`template`** (`template_animation_id`, 1 per direction), **`skeleton-v3`** (template posed onto the character; steadier identity, 2–4 per direction, beta), **`v3`** (`action_description`, `frame_count` 4–16 even), **`pixminimax`** (`frame_count` multiple of 4 up to 40, `subject_description`, `initial_pose`), `pro` (legacy, 10–25 per direction); `directions` (template default all, custom default south); `custom_start_frame`, `end_frame` (interpolation, one direction only); `keep_first_frame` (default true stores the reference as frame 0); `animation_group_id` + `animation_name` to add directions to an existing animation; `enhance_prompt` | One job per direction. Canvas grows with the motion (a 96 px character often animates at about 132 px) |
| `POST /animate-with-text-v3` (job) | `first_frame*` (≤256), `last_frame`, `action*`, `frame_count` 4–16 even, `drift_threshold` (colour de-flicker) | w·h·frames ≤ 524,288; animate any image, not only stored characters |
| `POST /animate-pixminimax` (job) | `first_frame*`, `last_frame`, `description*` (motion only), `frame_count` 4–40, `direction`, `view`, `subject_description`, `initial_pose`, `drift_threshold` | Returns frame_count + 1 frames (index 0 = input). Send all four caption fields to avoid an AI refusal |
| `POST /animate-with-skeleton-v3` (job, beta) | `description*` (looks), `action*`, `direction*`, `view`, `first_frame*`, `first_frame_keypoints*` (18 joints, x/y 0–1), `keypoints*` (one skeleton per frame, 3–15) | 3 frames = 2, 8 = 3, 15 = 4 generations; long clips are nearly free |
| `POST /estimate-skeleton` (sync) | `image` (≤256) | 0.1 generation; output feeds the skeleton endpoints |
| `POST /interpolation-v2` (Pro, job) | `start_image*`, `end_image*`, `action*`, `image_size*` (16–128) | 4–8 in-between frames |
| `POST /edit-animation-v2` (Pro, job) | `description*`, `frames*` (2–16), `image_size*` | Frames per call: 16–64 px → 16, 65–80 → 9, 81–256 → 4 |
| `POST /transfer-outfit-v2` (Pro, job) | `reference_image*`, `frames*`, `image_size*` (32–256), `additional_instructions` | One frame fewer than edit-animation per tier |
| `POST /vfx` (job) | `description*` (≤8000), optional `sprite` (+ `sprite_frames`, `sprite_fps`), `artist` `lite` (about 1 generation) or `pro`, `effect_id` + `conversation` to change an effect, `game_pack` | Returns GIF, spritesheet + JSON (pivot, anchor), optional game pack; quoted price charged on delivery |

**Template animations** (`template_animation_id`, humanoid): `backflip`, `breathing-idle`, `cross-punch`, `crouched-walking`, `crouching`, `drinking`, `falling-back-death`, `fight-stance-idle-8-frames`, `fireball`, `flying-kick`, `front-flip`, `getting-up`, `high-kick`, `hurricane-kick`, `jumping-1`, `jumping-2`, `lead-jab`, `leg-sweep`, `picking-up`, `pull-heavy-object`, `pushing`, `roundhouse-kick`, `running-4-frames`, `running-6-frames`, `running-8-frames`, `running-jump`, `running-slide`, `sad-walk`, `scary-walk`, `surprise-uppercut`, `taking-punch`, `throw-object`, `two-footed-jump`, `walk`, `walk-1`, `walk-2`, `walking`, `walking-2` … `walking-10`, `walking-4-frames`, `walking-6-frames`, `walking-8-frames`; plus `angry`, `attack`, `attack-back`, `attack-left`, `attack-right`, `bark` and others for quadrupeds. Ask `GET /characters/{id}` for the clips your character supports.

**Quality escalation** for an animation that looks wrong: template (1/direction) → skeleton-v3 (steadier identity) → v3 (custom text) → pixminimax (longer clips). Delete the failed animation first (`DELETE /characters/{id}/animations/{animation_group_id}`).

### 7.4 Rotation, objects and editing

| Endpoint | Key settings | Notes |
| --- | --- | --- |
| `POST /generate-8-rotations-v3` (job) | `first_frame*` (≤256, south-facing), `description` | Output order in `last_response.images` |
| `POST /generate-8-rotations-v2` (Pro, job) | `method` (`rotate_character`, `create_with_style`, `create_from_concept`), `image_size*` (32–168), `reference_image`, `concept_image`, `view` | Output order: S, SW, W, NW, N, NE, E, SE |
| `POST /rotate` (sync, legacy) | `from_image*`, `from_view`/`to_view`, `from_direction`/`to_direction`, `view_change` (±90°), `direction_change` (±180°) | 16/32/64/128 squares |
| `POST /create-1-direction-object` (job) | `description*`, `size` 16–256 (candidates: ≤42 → 64, ≤85 → 16, ≤170 → 4), `view` (`top-down`, `sidescroller`), `style_images`, `item_descriptions` (one per candidate) | 10–25 generations; several candidates enter `review`: keep with `POST /objects/{id}/select-frames` (`indices`) or `dismiss-review` |
| `POST /create-8-direction-object` (job) | `description*`, `size` 24–168, `view`, `reference_image` (rotate this exact object) **or** `style_image` **or** `style_object_id` | 10–25 generations |
| `POST /create-object-pro-flash` (job) | `description*`, `image_size`, `style_image`, `n_directions` 1 or 8, `source_image_id` / `first_frame` | 1 direction from an existing image is free |
| `POST /objects/{id}/animations` | `mode` `v3` (default, cheap) or `pro` (10–25 per direction), `animation_description`, `frame_count`, `custom_start_frame`, `end_frame`, `replace_existing` | 1-direction objects: do not pass `directions` |
| `POST /objects/{id}/states` | `edit_description*` | Variant of an object (broken, open, lit) |
| **`POST /map-objects`** (job) | `description*`, `image_size` (default 128), `view`, outline/shading/detail, **`background_image` + `inpainting`** (`{"type": "oval", "fraction": 0.6}`, rectangle, or custom mask) to draw an object **into an existing scene in its style** | Basic max 400×400, inpainting max 192×192; **auto-deleted after 8 h** |
| `POST /edit-image-pixen` (job) | `image*` (≤256 per side, multiple of 4), `description*` (≤500), `width`/`height` (re-render size) | 1 generation; keeps pose and style, changes only what you ask |
| `POST /edit-images-v2` (Pro, job) | `method` (`edit_with_text`, `edit_with_reference`), `edit_images*` (1–16), `image_size*` (32–512), `description` or `reference_image` | Batch edits stay consistent |
| `POST /edit-image-pro-flash` (job) | `image*`, `method` (`text`, `reference`), `description`, `reference_image`, `use_color_palette_correction` | Canvas never grows |
| `POST /inpaint-v3` (Pro, job) | `description*`, `inpainting_image*` (32–512), `mask_image*` (white = generate, black = keep), `crop_to_mask` | Precise local changes |
| `POST /inpaint-image-pro-flash` (job) | `image*`, `mask_image*` (pure black/white), `description*`, `context_image` + `bounding_box`, `output_method` | Keeps unmasked pixels exactly |

### 7.5 Tiles and maps

| Endpoint | Key settings | Notes |
| --- | --- | --- |
| `POST /create-tileset` (= `/tilesets`, job) | `lower_description*`, `upper_description*`, `transition_description`, `tile_size` (16/32; 64 needs `mode: "pro"`), `mode` (`standard`, `pro`), `transition_size` (0, 0.25, 0.5, 1.0 = cliffs; pro reads it as wall height), `view` (low/high top-down), `lower_base_tile_id` / `upper_base_tile_id` (chain tilesets so shared terrain matches), pro shape controls `raggedness`, `roundness` (0–2), `boundary_amplitude` (0–0.3), `step_slope`, `connect_diagonals`; standard `shape_style` (`square`, `round`) | Wang corner tiles: 16 tiles, or 25 at transition 1.0 (21 corner combos: match on `pattern_4x4`). Standard costs 1–4 generations (mean about 3), pro 15 (≤32 px) or 25 |
| `POST /create-tileset-sidescroller` (job) | `lower_description*` (platform material), `transition_description` (top layer: moss, snow), `transition_size`, `tile_size` 16/32 | Transparent background, flat platforms only; 2–3 generations |
| `POST /create-tiles-pro` (job) | `description*` (number the variations: "1). grass 2). stone"), `tile_type` (`hex`, `hex_pointy`, `isometric`, `oblique`, `octagon`, `square_topdown`), `tile_size` 16–128 (32 recommended), `tile_view` / `tile_view_angle` / `tile_depth_ratio`, `tile_feature` (`roads` 18-piece autotiles, `tileset` transition set, **`building`** kit: floor, connectable walls, doorways, pillar, stairs with `building_wall_description`, `building_floor_description`, `building_wall_tiles` 1–3), `style_images` | Independent variations or connectable sets |
| `POST /create-isometric-tile` (job) | `description*`, `image_size*` (16–64 area), `isometric_tile_shape` (`thin tile`, `thick tile`, `block`), `isometric_tile_size` 16/32 | Sizes above 24×24 look better |

### 7.6 UI, fonts, portraits and voice

| Endpoint | Key settings | Notes |
| --- | --- | --- |
| `POST /create-ui-asset` (Pro, job) | `description*` (style), `image_size` (192–688; aspect-gated: square ≤512, 16:9 ≤688×384, 4:3 ≤600×448), `pieces` (rounded_rect, circle, polygon on a 512-wide virtual canvas), `elements` (button, icon_button, toolbar, tab, panel, window, health_bar, avatar …), **`style_image`** (match your own approved mockup), `color_palette` | 10–25 generations |
| `POST /generate-ui-v2` (Pro, job) | `description*`, `image_size`, `concept_image`, `color_palette` | Buttons, bars, slots, dialogue boxes |
| `POST /generate-font-pro` (job) | `description*`, `weight*` (`Bold`, `Regular`), `glyph_px` 8/16/32/64, `font_name` | 80 glyphs (A–Z, a–z, 0–9, punctuation): atlas PNG + **`.ttf`** (`ttf_base64`); 15 generations |
| `POST /portrait-character-pro` (job) | `direction` (`portrait_to_character`, `character_to_portrait`), `image*`, `view`, `result_size` 16/32/48/64/128/160 | Bust ↔ full body, same identity |
| `POST /characters/{id}/portrait` | `image*` (16–256) | Free |
| `POST /vocal-animation` (job, paid plan) | `character_id` or `portrait`, `mood` (`neutral`, `happy`, `angry`, `sad`, `surprised`), `viseme_count` 3/5/7/12 (same for every mood) | Pay once per expression |
| `POST /talking-gif`, `POST /lip-sync` (free) | `text*` (≤500), `character_id` or `visemes`, `mood`, `frame_ms`, `hold_ms` | Lip-sync any Latin-alphabet line for free; `lip-sync` returns a frame plan to drive the mouth in the engine |

### 7.7 Cleanup and utilities

| Endpoint | Key settings | Notes |
| --- | --- | --- |
| `POST /unzoom` | `image*` (256–2048), `quantize` (0 auto, −1 keep, 2–256) | Recover native pixels from an upscaled image; result opaque |
| `POST /correct-pixelart` | `images*` (same size, corrected together), `strength` 0–1 (start 0.1) | Snaps stray and anti-aliased pixels; keeps size and alpha |
| `POST /reduce-colors` | `images*` (shared palette across frames, total ≤ 512×512 px), `num_colors` 2–256 **or** `palette_image`, `dithering` (`none`, 2x2, 4x4, 8x8), `dithering_strength` | One palette for a whole animation |
| `POST /remove-background` | `image*` (≤400×400 area), `image_size*`, `background_removal_task`, `text` hint | |
| `POST /resize` | `description*`, `reference_image*`, `target_size*` (16–200 area) | Pixel-aware resize; at most 2× up or 50% down per step |
| `POST /normal-map` | `image*` (8–512, strips up to 32 frames), `mode` `lite` (0.1) or `pro` (0.5), `kind` (`character`, `object`, `topdown`, `side`, `iso`, `ui`), `convention` (`opengl` for Godot/Unity/Phaser, `directx` for Unreal) | For lit 2D sprites |
| `POST /image-to-text` | `image*` (≤4096), `prompt` | About 0.09 generations; describe an approved image as a reusable prompt |
| `POST /enhance-pixen-prompt`, `/enhance-character-v3-prompt`, `/enhance-animation-v3-prompt` | the base description plus size, view, frames | Better prompts before a paid call |
| `GET /balance` | — | `{"credits": {"usd"}, "subscription": {"plan", "generations", "total"}}` |
| `GET /pro-flash/capabilities`, `GET /pro-flash/cost?operation=create|edit|inpaint|character|object&width=&height=&n_directions=` | — | Free; use before every Pro Flash run |

## 8. Errors, limits and retries

| Status | Meaning | Action |
| --- | --- | --- |
| 400 / 422 | Invalid request (size not a multiple of 4, too large, wrong combination such as `shape_style` with `mode: "pro"`) | Fix; do not retry unchanged. Oversize requests are refused before charging |
| 401 | Missing or invalid token | Stop |
| 402 | Insufficient generations or credits | Stop; tell the human |
| 403 | Not your asset, or the feature needs a (higher) paid plan | Stop |
| 404 | Unknown id | — |
| 409 | Conflict: direction already animated (`replace_existing`), ambiguous name (pass `animation_group_id`), still generating | Adjust |
| 410 | Generation failed permanently | Resubmit as a new job |
| 423 | Still generating | Wait `Retry-After`, poll again |
| 429 | Too many requests or too many concurrent jobs (Tier 3: up to 20) | Back off; wait for running jobs; do not cancel queued jobs to resubmit |
| 503 / 529 | Upstream busy or rate limit | Retry with backoff (20 s, 60 s, 120 s) |

Generation takes from seconds (sync endpoints) to 3–5 minutes (skeleton v3, PixMiniMax); 256 px template animations can take 30+ minutes per direction. Use long client timeouts.

## 9. PixelLab in the kit's reference-first pipeline

PixelLab can run the whole pipeline when a project chooses it (record the choice in `docs/specs/000-stack.md`):

1. **Explore** (`/gamedev-kit:new-asset`, step 1): `generate-image-v2` returns a grid of 4–64 candidates per call depending on size, ideal for a contact sheet of options; or 4–8 `create-image-pro-flash` / pixen calls with clearly different style prompts. The human picks.
2. **Style lock:** reuse the pick as `style_image` (Pro Flash, Pro, UI), `style_character_id` / `style_object_id` (Pro characters and objects), and the project palette as `target_palette` on every call.
3. **Characters:** pick or draw a clean **south-facing** sprite → `create-character-v3` (reference mode) or `create-character-pro-flash` with `source_image_id` → animations via template / skeleton-v3 / v3 / pixminimax → export with `/characters/{id}/spritesheet`. For a side-view-only game, request `view: "side"` and use the `east`/`west` directions.
4. **Scenes:** `create-tiles-pro` (`building` kits, tilesets), `map-objects` with `background_image` + inpainting to add props that match a room, `create-tileset` for top-down ground.
5. **UI:** `create-ui-asset` with the approved mockup as `style_image`; `generate-font-pro` for a pixel font with a real `.ttf`. The kit still prefers code-built UI (HTML/CSS) for anything with text.
6. **Cleanup:** `reduce-colors` across all frames with `palette_image` (one palette per animation), `correct-pixelart` at strength 0.1, then the kit's lint and a manual Sprite Grid pass. Never AI-upscale; never rescale pixel art.
7. **Log:** every call's `usage`, endpoint, model, prompt hash, seed and ids go to `build/gen/log.jsonl`, and every approved or shipped file to `assets/manifest.json` with licence `PixelLab subscription: commercial use, no model training on output`.

Use the **MCP** tools for exploration in a conversation, and **`tools/gen_image.py --provider pixellab`** (recipes in `art/recipes/`) for anything repeatable.

## 10. Recommended client pattern

1. Key from `PIXELLAB_API_KEY`; never print it.
2. Check `GET /balance` and, for Pro Flash, `GET /pro-flash/cost` before a run; refuse and ask the human above the daily budget.
3. Validate sizes locally (multiples of 4, area limits per endpoint and tier) so nothing is refused after upload.
4. Dry-run by default: print the request with images replaced by file names and the estimate.
5. Submit; for jobs poll `GET /background-jobs/{id}` every 5–10 s with a long overall timeout; retry 429/503/529 with backoff; never retry 400/401/402/403 unchanged.
6. Decode `base64` images and save them immediately; download library assets (map objects vanish after 8 h).
7. Log `usage`, ids and the seed to an append-only log.

### Minimal Python call (pixen, synchronous)

```python
import base64, json, os, urllib.request

def pixellab(path, body):
    req = urllib.request.Request(
        "https://api.pixellab.ai/v2" + path, data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + os.environ["PIXELLAB_API_KEY"]})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)

resp = pixellab("/create-image-pixen", {
    "description": "scrap-metal robot boxer, side view, facing right",
    "image_size": {"width": 64, "height": 64},
    "view": "side", "direction": "east", "no_background": True})
open("robot.png", "wb").write(base64.b64decode(resp["image"]["base64"]))
print(resp.get("usage"))
```

For background jobs, take `background_job_id` from the response and poll `GET /v2/background-jobs/{id}` until `status == "completed"`; images are in `last_response["images"]` as image objects.

## 11. Quick reference

| Task | Endpoint |
| --- | --- |
| One sprite, fast | `POST /create-image-pixen` |
| Many style candidates in one call | `POST /generate-image-v2` (small sizes) |
| One best image / reusable south frame | `POST /create-image-pro-flash` |
| Character with 8 directions | `POST /create-character-v3` (or `-pro-flash`, `-pro` with `style_character_id`) |
| Animate a character | `POST /characters/animations` |
| Animate any image | `POST /animate-with-text-v3`, `/animate-pixminimax` |
| Outfit or state variant | `POST /create-character-state`, `/transfer-outfit-v2` |
| Prop that fits a scene | `POST /map-objects` with `background_image` |
| Building kit / tiles | `POST /create-tiles-pro` (`tile_feature: "building"`) |
| Top-down ground tileset | `POST /create-tileset` |
| Platformer tileset | `POST /create-tileset-sidescroller` |
| UI panel / font | `POST /create-ui-asset`, `/generate-font-pro` |
| Portrait and lip-sync | `/portrait-character-pro`, `/vocal-animation`, `/talking-gif` |
| Effects | `POST /vfx` |
| Cleanup | `/unzoom`, `/correct-pixelart`, `/reduce-colors`, `/remove-background` |
| Job status | `GET /background-jobs/{id}` |
| Balance / Pro Flash price | `GET /balance`, `GET /pro-flash/cost` |

Full documentation: https://api.pixellab.ai/v2/docs · https://www.pixellab.ai/docs · support: support@pixellab.ai · Discord: https://discord.gg/pBeyTBF8T7

Further sources: plan prices from https://www.powerfulai.tools/tool/details/pixellab and https://app.cinevva.com/guides/ai-pixel-art-generators (secondary; confirm on the site); terms at https://www.pixellab.ai/termsofservice.
