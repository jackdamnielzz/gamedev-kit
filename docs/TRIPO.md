# Tripo (3D generation) — a complete working reference

> **Master copy:** the GitHub repo `jackdamnielzz/gamedev-kit`, folder `docs/`. Copies elsewhere follow the repo; change the repo first.

A portable guide for an AI agent or developer who uses Tripo to make game assets: characters (humanoids, undead, monsters), quadrupeds and props. Part A (sections 1–4) is the API v3 reference so code can be written without guessing. Part B (sections 5–9) is how to get good results and how Tripo fits the kit's reference-first pipeline (approved reference image → image-to-3D → Blender clean-up and render; see `AI-ASSET-WORKFLOW.md`, Route B and "3D generation").

Sources: the official developer docs at https://developers.tripo3d.ai/en/docs (platform.tripo3d.ai redirects there), the pricing and changelog pages, the Python SDK source, plus vendor and reseller material (Scenario) and general knowledge for the Blender side. **Verified on:** documentation research of **4 November 2026**; no live API call has been made yet (see section 10). Enum values were read through a summarising fetch: re-verify critical ones against the docs before depending on them. Tripo marketing pages often return 403; treat web-plan details as unverified.

**Label convention.** Plain statements are sourced. Anything marked **(inference)** is reasoning or general knowledge, not a documented Tripo fact; test it before relying on it.

---

## 1. Overview: what Tripo is for in the kit

Tripo (Tripo3D, VAST AI Research) turns an image (or several views, or text) into a textured 3D model, and also retopologises, rigs and animates it. In the kit it is **Route B** for organic assets: creatures, characters, anything code and Blender primitives cannot sculpt.

| Need | Use |
| --- | --- |
| Hard-surface props, architecture, simple shapes, anything a few primitives can build | **Route A**: Blender primitives from code. Free, exact, palette-controlled |
| Organic character, undead, monster, hound, ornate prop; needs rig and animation | **Tripo** (default) |
| Same, free and self-hosted, no rig | TRELLIS.2 (MIT, needs 24 GB VRAM on Linux) |
| Same, more mesh-tuning control, cheap rig and animation | Meshy (see `AI-ASSET-WORKFLOW.md`); a third-party comparison says Meshy gives more mesh control, Tripo is cheaper and faster with fewer decisions |
| Pixel-art look directly | PixelLab (`PIXELLAB-API.md`), not Tripo |

Rules of thumb:

- Input is always an **approved reference image**, never a raw text prompt (text-to-model exists but loses control; use it only for throwaway tests).
- Treat Tripo output as a **base mesh**: expect clean-up, re-materialing and a polygon budget pass in Blender.
- **Use v3 only.** The v2 API (`/v2/openapi/...`) was shut down on **2026-10-31**. Old v2 snippets, old SDK versions (`tripo3d` 0.x) and the old `POST /task` + `type` pattern no longer work. v2 and v3 shared API keys, so existing keys still work.

## 2. Account, plans, credits and licence

- **API billing is pay-as-you-go.** 1 credit = $0.01; top-up from $1. Credits are frozen at task creation, consumed on success, returned on failure or cancel ("failed and cancelled tasks are not charged"). From 2026-12-01 the console shows USD, but the API still returns credits.
- **Key:** create it in the developer console; it starts with `tsk_`. Store it in the user environment variable **`TRIPO_API_KEY`** (the Python SDK reads this name). Never print, log or commit it. Windows: `[Environment]::SetEnvironmentVariable('TRIPO_API_KEY', '<key>', 'User')`, then restart the editor. Never sell or transfer keys (terms).
- **Web subscription plans: unverified.** The official plans page returned 403. Third-party sources conflict: names Free/Pro/Max/Team (some: Basic/Professional/Advanced/Premium), free plan 200–300 credits per month, Pro about $19.90 per month for about 3,000 credits, top plan 25,000–45,000 credits, one tracker claims a top-plan price rise on 2026-08-24 (unconfirmed). Whether web-plan credits and API credits are separate is not documented (likely separate: **unverified**). Enterprise: business@tripo3d.ai.
- **Licence** ([terms](https://developers.tripo3d.ai/en/terms)):
  - **Free users:** "Tripo retains all rights", including to use, copy and monetise inputs and outputs (§5.2.1). Not usable for shipped assets.
  - **Paid users:** you generally hold the rights to inputs and outputs (§5.2.2); Tripo may display content royalty-free and non-exclusively to run the service but **will not use inputs or outputs as training data**. Outputs are not exclusive (§3.2). Commercial use is allowed for lawful purposes.
  - **Prohibited:** using outputs to build a model or service that competes with Tripo's operator (Holymolly); reverse engineering; automated extraction; reselling access to the 3D foundation model service.
  - A "free plan is CC BY" claim from consumer pages is **not verified** on the API terms.
- **Kit rules:** generate every shipped asset on a **paid** plan or paid API credits; record "Tripo, paid, no-competing-model-training" in the asset manifest licence field; set `ai_pixels_shipped`/AI-disclosure flags as the manifest requires. API use is pay-as-you-go, so paid terms most likely apply **(inference)**; confirm with Tripo before a commercial release.

## 3. API v3 basics

### 3.1 Base URL, auth, create

- Base URL `https://openapi.tripo3d.ai/v3` (China: `openapi.tripo3d.com`, SDK flag `IS_GLOBAL=False`).
- Header `Authorization: Bearer $TRIPO_API_KEY`.
- v3 has **dedicated endpoints per task** (no universal `POST /task` with a `type`). Create response: `{"code":0,"data":{"task_id":"..."}}`.
- Minimal example:

```
POST /v3/generation/image-to-model
{"input":"file_abc123","model":"P2-20260801","face_limit":8000}
```

### 3.2 Files and the `input` string

- Upload: `POST /v3/files`, multipart field `file`. Images JPEG/PNG up to 20 MB; models GLB/GLTF/FBX/OBJ/STL up to 150 MB; above 60 MB use `POST /v3/files/presign`. Returns `file_token` (`file_abc123`). Token lifetime is not documented: upload right before use.
- **`input` is a single string everywhere in v3**: a `task_id`, a `file_token` or a public URL; the type is inferred. (Multiview takes an array, see 4.1.) The v2 per-source fields (`file`, `object`, `original_model_task_id`) are gone. Renames: `create_time` → `created_at`, `consumed_credit` → `credits_consumed`.
- Image inputs: PNG/JPEG/WebP, at least 256 px, up to 20 MB.

### 3.3 Polling, statuses, output

- `GET /v3/tasks/{task_id}` returns `data`: `task_id`, `type`, `status`, `progress` (0–100), `error_code`, `error_message`, `output` (success only), `credits_consumed` (decimal), `created_at`, `completed_at`. The top-level `code` is the request code, distinct from `error_code`.
- Statuses: `queued` → `running` → `success` / `failed` / `cancelled`. Legacy `banned` and `expired` are reported as `failed`; treat any other value (for example `unknown`) with a bounded wait.
- Poll every **2 s, at most 1 request per second**. For many tasks use `POST /v3/tasks/list` with `task_ids` instead of many GETs.
- Output keys: `model_url` (GLB unless the task chose another format), `rendered_image_url`; import and post-process tasks on tokens/URLs also return `normalize_scale` and `normalize_translation` (normalised = original × scale + translation). The v2 keys `pbr_model_url` and `base_model` are not in v3.
- **Output URLs are short-lived (quick start says 5 minutes; the lifecycle page says unspecified). Download to disk immediately and never store the URL.**
- Balance: `GET /v3/account/balance` → `balance`, `frozen` (decimals, parse as decimal not int). Usage: `GET /v3/account/usage` (windows up to 31 days).

### 3.4 Webhooks (alternative to polling)

- Configure in console Settings → Webhooks: HTTPS URL; the signing secret `whsec_...` is shown once.
- Events: `task.completed`, `task.failed`, `balance.low`. Body: `id`, `type`, `created_at`, `data` (`task_id`, `type`, `status`, `output`, or `error_code`/`error_message`).
- Headers: `Tripo-Webhook-Id`, `Tripo-Webhook-Delivery` (use to dedupe), `Tripo-Webhook-Event`, `Tripo-Webhook-Signature: t=<unix>,v1=<hex>`.
- **Verify:** `v1` = lowercase hex HMAC-SHA256 of the string `"<t>.<raw body>"` with the secret. Use the raw bytes of the body (not re-serialised JSON), compare in constant time, reject if `t` is more than 5 minutes off.
- Respond 2xx within about 5 s. Retries on non-2xx or timeout; count and interval are not specified.

### 3.5 Limits and retries

- Rate limits are per API key; no numbers are published; generation endpoints are lower than query endpoints. Headers `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` (unix seconds). HTTP 429, code `1007`.
- **Concurrency per account, per category (defaults):** H-series generation 10; P-series generation 5; image generation 1; animation (rig-check, rig, retarget) 10; model processing (texture, convert, refine) 5; mesh ops (segment, complete, retopology) 10. A full category returns 429 + code `2000` + `Retry-After`. Higher limits via support.
- Backoff: 1 s, 2 s, 4 s ... capped at 32 s, at most 5 retries; **retry only 429 and 500**. A task may have been created even if the response was lost: check `tasks/list` before re-creating **(inference from the docs' note)**.

### 3.6 Error codes

| HTTP | Code | Meaning |
| --- | --- | --- |
| 401 | 2, 1002 | Authentication failed |
| 500 | 1000, 1001 | Server error (retry) |
| 400 | 1003 | Malformed body |
| 400 | 1004 | Invalid or missing parameter (also: bad combination such as `generate_parts` with texture on, `fast` texture without v3.5) |
| 429 | 1007 | Rate limit |
| 429 | 2000 | Concurrency limit for this category |
| 404 | 2001 | Task not found |
| 400/404 | 2002 | Unsupported task type |
| 400 | 2003 | Empty input file |
| 400 | 2004 | Unsupported file type |
| 400 | 2008 | Content policy violation |
| 403 | 2010 | **Insufficient credits** |
| 400 | 2015 | Model or task version deprecated |
| 400 | 2018 | Model too complex |
| 404 | 4001 | Endpoint not found |

HTTP 403 covers both "no permission" and "no credits": tell them apart by the code (2010 = credits).

### 3.7 SDKs, plugins, MCP

- Python `pip install tripo3d==1.0.0` (3.8+; 0.x broke at the v2 shutdown): `TripoClient`, `wait_for_task(task_id, polling_interval=2.0, timeout=None)`, `download_task_models`, `rig_model`, `retarget_animation`, `convert_model`, `smart_lowpoly`. Python SDK 1.0 raises "retired" for `refine_model` and `stylize_model`. SDK defaults for the model version may still be `v2.5-20250123`: **always pass `model` explicitly**. Also JS `@vastai/tripo-sdk`, Go, Rust, Java (source only).
- Plugins (zip downloads): Unity, Unreal 5.6, Blender 0.7.3 (3.0+), **Godot 0.02 (Godot 4.4+; text and image tasks)**, Cocos Creator, ComfyUI. Godot zip: https://cdn-web.tripo3d.ai/plugin/tripo-godot.zip. Also a Tripo CLI and the Tripo DCC Bridge (manual UI push from Tripo Studio into one running Blender; not for automation).
- `VAST-AI-Research/tripo-mcp` is a Blender-bridge only MCP server, alpha, last pushed about April 2025, may not use v3. Prefer REST/SDK scripts in the repo plus headless Blender.

---

## 4. Endpoints and parameters

Endpoint map: `/generation/{text-to-model, image-to-model, multiview-to-model, text-to-image, image-to-image, image-to-multiview, edit-multiview, image-to-splat, image-to-depth}`, `/models/{import, convert, texture, refine, stylize}`, `/mesh/{segment, smartsegment, complete, decimate, uv}`, `/animations/{rig-check, rig, retarget}`. Returned task `type` strings: `text_to_model`, `image_to_model`, `multiview_to_model`, `texture_model`, `convert_model`, `import_model`, `animate_prerigcheck`, `animate_rig`, `animate_retarget`, `mesh_segmentation`, `mesh_completion`, `highpoly_to_lowpoly`, `mesh_uv`.

### 4.1 Generation (text, image, multiview)

`model` is **required**.

| Series | `model` string | Notes |
| --- | --- | --- |
| H (general) | `v3.1-20260211` (recommended), `v3.0-20250812`, `v2.5-20250123` | Best detail; full parameter set below |
| P1 (low-poly) | `P1-20260311` | 50–20,000 faces; fast |
| P2 (game topology) | `P2-20260801` | Native quad; 48–50,000 triangles or 48–25,000 quads; "preview, may error" per a reseller |

Parameters, H series:

| Parameter | Values / default | Notes |
| --- | --- | --- |
| `prompt`, `negative_prompt`, `image_seed` | text only; prompt ≤1024, negative ≤255 chars | `image_seed` seeds the internal text-to-image |
| `input` (image) | file_token, URL, or task_id of a text_to_image/image_to_image task | |
| `input` (multiview) | array: `[{"front":..},{"back":..}]` (keys front/left/back/right, front required, at least 2 views, order irrelevant) **or** 4 positional strings `[front,left,back,right]` with `""` to skip **or** `[{"task_id":..}]` from image_to_multiview/edit_multiview | values: URL, file_token, `{url}`, `{file_token}` |
| `enable_image_autofix` | false | |
| `texture_alignment` | `original_image` (default) \| `geometry` | |
| `orientation` | `default` \| `align_image` | only with texture on |
| `model_seed`, `texture_seed` | random if unset | reuse to keep shape across quality passes |
| `face_limit` | adaptive if unset | see caps below |
| `texture` / `pbr` | true / true | `pbr=true` forces `texture=true` |
| `texture_quality` | `fast` \| `standard` (default) \| `detailed` \| `extreme` (8K) | v3.0+ only; `fast` needs `texture_version=v3.5-20260815` |
| `texture_version` | `v3.5-20260815` \| `v3.0-20250812` \| `v2.5-20250123` | derived from `model` if unset |
| `delight` | true | removes baked lighting; v3.5 texture only |
| `geometry_quality` | `standard` \| `detailed` (Ultra) | v3.0+; not v2.5 |
| `auto_size` | false | real-world metres; v3.0+ |
| `quad` | false | forces FBX output; default 10,000 faces if no `face_limit`; v3.0+ |
| `smart_low_poly` | false | v3.0+ |
| `generate_parts` | false | requires `texture=false` **and** `pbr=false` explicitly, else error 1004; incompatible with quad and smart_low_poly. A reseller says 2.5 only: unverified |
| `compress` | `geometry` (meshopt) | v3.0+ |
| `export_orientation` | `+x` (default), `-x`, `-y`, `+y` | avoid if post-processing; a wrong value still returns success |
| `export_uv` | true | |

P series takes: `input`, `enable_image_autofix`, `texture_alignment`, `orientation`, `model_seed`, `face_limit`, `texture`, `pbr`, `texture_seed`, `texture_quality`, `texture_version`, `delight`, `auto_size`, `export_uv`, `export_orientation`, and `quad` (P2 only). No `geometry_quality`, `smart_low_poly`, `generate_parts` or `compress` are listed for P. P-series text and multiview pages were not read; a reseller says P2 multiview accepts front plus any of left/back/right.

**`face_limit` caps:** triangles v3.1 1,500,000 standard / 2,000,000 Ultra; v3.0 1,000,000 / 2,000,000; v2.5 500,000; quad 150,000; with `smart_low_poly`: triangles 500–20,000, quads 500–10,000. P1 50–20,000; P2 triangles 48–50,000, quads 48–25,000 (docs suggest starting around 150 for simple and 250 for complex P-series objects). Docs guidance: game-ready 50k–100k, web/mobile 10k–50k.

### 4.2 Texture, convert, import

- **Texture** `POST /v3/models/texture`: `input` (task_id/file_token/URL, model file up to 150 MB), `model` (default `v3.0-20250812`; `v3.5-20260815`, `v2.5-20250123`), `texture_prompt` {`text`, `style_image`, `image`, `images` (front/left/back/right, front required, at least 2)} (text/image/images are mutually exclusive; `style_image` only with `text`), `pbr` (true), `texture_seed`, `texture_alignment`, `texture_quality`, `part_names` (from segmentation), `compress`, `bake` (true), `delight` (true). Works best on plain untextured meshes.
- **Convert** `POST /v3/models/convert`: `input`, **`format`** required (`GLTF`, `FBX`, `USDZ`, `OBJ`, `STL`, `3MF`). Options: `quad` (forces FBX), `force_symmetry` (needs quad), `face_limit` (original kept if omitted), `flatten_bottom`, `flatten_bottom_threshold` (0.01), `texture_size` (4096), `texture_format` (`JPEG` default, `PNG`, `WEBP`, `BMP`, `DPX`, `HDR`, `OPEN_EXR`, `TARGA`, `TIFF`), `bake` (true), `pack_uv`, `export_vertex_colors` (OBJ/GLTF), `pivot_to_center_bottom`, `scale_factor` (1), `with_animation` (true), `animate_in_place`, `part_names`, `export_orientation`, `fbx_preset` (`blender` default, `3dsmax`, `mixamo`, `bake_scale`), `texture_packaging` (`embedded` \| `zip`, FBX only). Which options trigger "advanced" pricing is not stated.
- **Import** `POST /v3/models/import`: `input` (file_token or URL; GLB/GLTF/FBX/OBJ/STL up to 150 MB). Lets you bring a Blender-cleaned mesh back for rigging.
- **Refine / stylize:** the migration page says they exist, the Python SDK 1.0 calls them retired. **Treat as unavailable.** Legacy stylize only offered LEGO, Voxel, Voronoi, Minecraft: no use for style consistency anyway.

### 4.3 Mesh operations

- **Retopology / smart low-poly** `POST /v3/mesh/decimate` (type `highpoly_to_lowpoly`): `model` `v3.0` (supports `quad`, `smart_uv`, `bake`, `part_names`) \| `v2.0` (default, Smart Retopology) \| `v1.0` (basic; `face_limit` required, no bake or part_names). `face_limit`: triangles 500–20,000, quads 500–10,000 (v2/v3; adaptive if omitted). `smart_uv` is v3.0 only (else 1004). A vendor note says quad retopo can overshoot the target by about 17%.
- **Smart UV** `POST /v3/mesh/uv` (returns a UV atlas preview).
- **Segmentation** `POST /v3/mesh/segment`: `model` `v1.0-20250506` (default, geometric) \| `v2.0-20260430` (Beta, semantic). v2 only: `segmentation_granularity` (`simple` \| `balanced` default \| `detailed`), `split_by_connectivity` (true), `ref_image` (overrides the two). Works best on clearly separated parts (a character holding a weapon). **Smart segmentation** `/mesh/smartsegment` (accepts a task_id since 2026-11). **Completion** `/mesh/complete`: SDK params `part_names`, `completion_mode` (values not verified).

### 4.4 Rigging and animation endpoints

- **Rig-check** `POST /v3/animations/rig-check`: **free**; accepts GLB/FBX/OBJ/STL; returns whether the model is riggable and the recommended `rig_type` (response schema not documented). Run it before every rig.
- **Rig** `POST /v3/animations/rig`: `input` (task_id/file_token/URL; GLB/FBX/OBJ/STL up to 150 MB), `model`, `rig_type`, `spec`, `out_format` (`glb` \| `fbx`).

| Rig `model` | Use |
| --- | --- |
| `v1.0-20240301` (default) | Biped only; unlocks the 90+ extended biped presets |
| `v2.5-20260210` | Non-humanoid creatures (bipeds supported but not recommended) |
| `v3.0-20260909` | **Recommended for humanoids**; opt-in (set explicitly); adds `others` rig type and more specs |

`rig_type`: `biped` (default), `quadruped`, `hexapod`, `octopod`, `avian`, `serpentine`, `aquatic`, `others` (v3.0 only). `spec` (bone naming, biped only): `tripo` (default), `mixamo`; v3.0 adds `actorcore`, `unity`, `unreal`, `vrm`. Heavy meshes fail: keep under about 300k polygons (reseller guidance).

- **Retarget** `POST /v3/animations/retarget` (type `animate_retarget`): `input` = the task_id of the **rigged** model (the raw generation task id fails), `animation` (one) XOR `animations` (array, max 5), `out_format` (`glb` default \| `fbx`), `export_with_geometry` (true), `animate_in_place` (false), `bake_animation` (deprecated, ignored). One file per request; with a batch expect separate outputs or a combined file: inspect the first result **(inference)**.

### 4.5 Animation presets

- **Basic set, rigs v2.5 and v3.0** (11 universal + 5 locomotion): `preset:idle`, `preset:walk`, `preset:run`, `preset:dive`, `preset:climb`, `preset:jump`, `preset:slash`, `preset:shoot`, `preset:hurt`, `preset:fall`, `preset:turn`; `preset:quadruped:walk`, `preset:hexapod:walk`, `preset:octopod:walk`, `preset:serpentine:march`, `preset:aquatic:march`.
- **Extended set, rig v1.0 only** (biped, prefix `preset:biped:`; v2.5/v3.0 rigs do **not** get these): afraid, agree, angry_01–03, bow, box_01–03, cast_a_spell, cheer, chop, clap, climb, complain_01–02, cry, dance_01–06, defeat_02, defeat_03, depressed, dig, dive, fall, flee_01–02, flip, fold_arms, frightened, front_kick_01–02, frustrated_01–02, greet_01–04, hit_to_body_01–02, hit_to_head, hit_to_side, hit_to_stomach, hug, hurt, idle, jump_down, jump, laugh_01–02, lift_heavy, look_around, press-up, run_upstairs, run, scared_01–02, scratch, shoot, shovel, sing_01–04, sit, slash, sob, standing_relax, swagger, swim, turn, victory_celebration, wait, walk, warm_up, wave_goodbye_01–02, plus sports/misc (basketball_shot, dribble, football_*, golf, jump_rope_01–02, pitch_baseball, volleyball, surf, make_a_call_01–02, play_mobile_game, play_video_game, freaky, heart_pose, cross_body_crunch, crossover_dribble, fire). Useful for an ARPG: `slash`, `cast_a_spell`, `hit_to_*`, `hurt`, `flee_*`, `frightened`, `lift_heavy`, `front_kick_*`, `look_around`, `wait`, `victory_celebration`.
- **There is no `death`/`die` preset.** Closest: `preset:biped:defeat_02`, `defeat_03`, `fall`, `hurt` (not documented as death clips). Alternatives in section 6.4.
- **ID format is inconsistent in the docs** (quick start uses the `preset:` prefix, other pages bare names): verify with the first live call.

### 4.6 Costs per call (credits; 1 credit = $0.01)

| Call | Credits | Notes |
| --- | --- | --- |
| Text-to-model, H series | 10 no texture / 20 standard texture | |
| Image-to-model or multiview, H series | 20 / 30 | image-to-multiview generation 10; edit-multiview 5 per image |
| Add-ons (H series) | HD texture +10, Ultra 8K texture +20, HD geometry +20, quad +5, smart low-poly +10, generate parts +20 | An AWS listing shows other numbers: ignore |
| P2 generation | 100 no texture; 110 / 120 / 130 with standard / detailed / extreme texture | P1 price not found; text-to-model P-series price not found |
| Texture (separate call) | 10 fast/standard, 20 HD, 30 8K | |
| Convert | 5 basic, 10 advanced | |
| Retopology | v3 35 triangles / 40 quad; v2 30; v1 10 | |
| Smart UV | 20 | |
| Segmentation | 40 | smart segmentation 85 (image) / 55 (model) |
| Part completion | 50 | Quick Cap 30 |
| Rig-check | **0** | |
| Auto-rig | 25 | |
| Retarget | 10 **per animation** | |

Image generation per model and size is priced separately (the fetch was garbled). Prices rose in 2026; read https://developers.tripo3d.ai/en/pricing before budgeting.

---

## 5. Getting quality

### 5.1 Input image preparation

Sourced (vendor and reseller guidance, mostly generic image-to-3D advice):

- Input quality is the main driver of output quality. One clear subject, **background removed** (background elements become stray geometry), simple or transparent background, front or 3/4 view.
- 1024×1024 or larger; upscale 2×/4× when below that. Avoid heavy JPEG compression; prefer PNG.
- Even lighting, no strong cast shadows, no multiple light sources. Clean stylised art converts better than rough sketches or very detailed photos.
- Tripo 3.0 added "Pose Control" for A/T pose on characters (web feature; API exposure unverified). `delight` removes baked lighting from the result (v3.5 texture only).
- Keep all views of one character in the same pose.

**(inference)** for this kit: neutral grey or transparent background, flat even lighting, A-pose with arms clear of the torso and legs apart so limbs do not merge (helps later rigging), hands empty (weapon as a separate prop), cape and loose cloth kept short or shown stiff, hound in a neutral standing pose with all four legs visible.

### 5.2 Making reference sheets (the kit's image route)

Use the kit's image models through NanoGPT (see `AI-ASSET-WORKFLOW.md`): Nano Banana for the first concept and for edits, GPT Image as the alternative. Sourced: take the front concept as the anchor and generate the other angles with an image-edit model, with prompts like "same character, side view, neutral pose, same style and proportions"; a reseller says GPT Image 2 handles this particularly well. No Tripo-specific Nano Banana prompt guidance exists in the sources: the points below are **(inference)**.

1. Generate the front view first and get it approved (this is the reference the kit's gate compares renders against).
2. Edit-generate back, left and right views from the approved front, one image per call, same A-pose, same background, same crop height. Check silhouette height and proportions match across the four.
3. Remove the background, upscale, save under `art/refs/<asset>/{front,left,back,right}.png`.
4. Keep one locked style block (prompt text plus a style reference image) for the whole cast.

### 5.3 Single image vs multi-view

- Multi-view (front/left/back/right) removes most "hallucinated back of the head" clean-up and is the choice for hero characters. A reseller reports it saves "minutes instead of hours" of back-side clean-up. Tripo 3.0 multiview is listed as deprecated.
- Single image on 3.1 is fine for props, environment and secondary characters.
- P2 multiview accepts front plus any combination of the others; front + back is the safest minimum (reseller). The v3 API requires at least two views.
- Without HD texture, Smart Low Poly, quad or PBR a reseller calls the result a preview.

### 5.4 Model and settings per asset class

Starting points. Models and settings are sourced; the numeric face budgets are **(inference)** and must be tuned by eye, because no official per-asset recommendation exists.

| Asset class | Model and input | Settings | Face budget (inference) |
| --- | --- | --- | --- |
| **Hero character** (family members, bosses) | `v3.1-20260211` multiview (4 views) | `texture_quality: detailed` or `extreme`, `geometry_quality: detailed`, `pbr: true`, `delight: true` (v3.5), `smart_low_poly: true` or `quad`; fixed seeds | Pre-rendered sprites: 15k–30k triangles. Real-time: 8k–15k |
| **Secondary character** (rank-and-file undead, NPCs) | `v3.1` single image, or `P2` | `standard` texture, `smart_low_poly: true` | Sprites: 5k–15k. Real-time: 3k–8k |
| **Quadruped / monster** (hounds) | `v3.1` or P2 multiview, neutral standing pose | as secondary; rig with `quadruped` | Sprites: 8k–20k. Real-time: 4k–10k |
| **Prop** (weapons, chests, torches) | `v3.1` single image, or P1/P2 for speed | `standard` texture, `smart_low_poly`, or P2 `face_limit` 150–2,000 | Sprites: 500–3,000. Real-time: 500–5,000 |

Why so low for sprites: detail is invisible once the render is downscaled to 64–128 px, so face count mainly costs rig time and weight problems. Rigging fails on very heavy meshes (keep under about 300k polygons, a hard upper bound). For real-time use the docs' own range is 10k–50k for web/mobile and 50k–100k for game-ready PC: the table is deliberately well under that for a 640×360 isometric game. Reseller guidance: P1 for speed, P2 for cleanest topology and quad export, 3.1 for maximum quality.

### 5.5 Texture, PBR and delight

- PBR on (default) gives Principled-BSDF-ready maps. When PBR is on, some texture settings may be ignored (reseller). For this kit, plan to **re-material in Blender** anyway (section 7), so geometry quality and the base colour matter most; metallic and roughness are secondary.
- `delight: true` with `texture_version: v3.5-20260815` when the reference has painted shading or cast shadows. Even reference lighting still matters.
- `texture_quality: fast` + v3.5 + delight for drafts; `standard` for secondary assets; `detailed`/`extreme` for heroes. Extreme (8K) costs +20 credits on generation and is rarely visible at sprite size **(inference)**.
- Retexturing a single part: segment, then texture with `part_names`.

### 5.6 Iteration strategy

Sourced: draft with v3.5 + `fast` + delight, then rerun with the **same seed** at standard/HD/8K; seed reuse keeps the shape across quality passes (not across assets). **(inference)** for the loop:

1. Draft at the cheapest setting (H series, no texture, or P1) to judge silhouette and proportions only; 20 credits or less per try.
2. Change the **reference image**, not the settings, when shape is wrong. Fix `model_seed` once the shape is right.
3. Re-run with the fixed `model_seed` and `texture_seed` at final quality (and `face_limit` set) for the one you keep.
4. Log task ids, seeds, model strings and credits in the asset manifest so any asset can be regenerated.

### 5.7 Cast-wide style consistency

No Tripo feature gives cross-asset style consistency (stylize is retired or limited to LEGO/Voxel/Voronoi). Consistency has to come from the 2D concept stage **(inference, supported by the absence of a Tripo method)**: one locked style prompt and style reference for every concept sheet, the same lighting and palette in all references, the same Tripo model, texture version and quality for the whole cast, and above all the Blender re-material step (section 7), which forces every asset onto the project palette and lighting rig. An optional style-trained model (Scenario) is covered in section 8.

### 5.8 Failure modes and fixes

Sourced issues: fused joints, messy topology that needs retopology before rigging (competitor review, biased), melded hands and missing limbs (user reports). Sourced fixes: multi-view, segmentation, retopology, manual edge-loop clean-up at joints and face. The rest is **(inference)** and unsourced.

| Problem | Fix | Source |
| --- | --- | --- |
| Back of the character is invented or wrong | Multi-view with a real back reference | Sourced |
| Fused joints, melded hands, missing limbs | Multi-view; A-pose reference; retopology; Blender clean-up; check at final sprite size before fixing | Sourced |
| Messy topology | `smart_low_poly`, P2 quad, or `/mesh/decimate` v3.0 with `quad` | Sourced |
| Weapon fused to the hand | Hands-empty reference; generate the weapon as a separate prop and parent it to a hand bone in Blender | Inference |
| Cape, claws, hair come out thin or broken | Make them stiffer and shorter in the reference, or model separately; segment and treat as a rigid part | Inference |
| Baked-in lighting or shadows in the texture | Even reference lighting, `delight` (v3.5), or discard the texture and re-material | Sourced + inference |
| Asymmetry errors | Reference sheets with matching left/right; `force_symmetry` on quad convert | Inference |
| Wrong scale or facing | Do not use `export_orientation`; normalise scale in Blender; check after import | Inference |
| Error 1004 on a settings combination | See the notes in 4.1 (`fast` needs v3.5; `generate_parts` needs texture and pbr false; `smart_uv` is retopology v3.0 only) | Sourced |
| Rig fails or looks bad | Run rig-check; reduce faces; use `rig_type` from rig-check; fix weights in Blender | Sourced + inference |
| Quad retopology overshoots the face target | Aim about 15% under | Sourced |

---

## 6. Rigging and animation

### 6.1 Which rig for which asset

- **Humanoids and undead:** rig `model: v3.0-20260909`, `rig_type: biped`, **`spec: mixamo`**. The Mixamo bone names are what make free Mixamo and Quaternius clips map almost automatically in Blender.
- **Quadrupeds and creatures:** `model: v2.5-20260210`, `rig_type: quadruped` (or hexapod, octopod, avian, serpentine, aquatic as the creature requires). Mixamo is humanoid-only, so this is Tripo's differentiator (vendor claim, not independently tested).
- **Need the 90+ extended biped presets:** `model: v1.0-20240301` (biped only). It trades away the newer rigs.
- **Order of calls:** generate → (optional Blender clean-up → `models/import`) → **rig-check (free)** → rig → retarget presets. Bad rig-check result: fix the mesh first, do not pay for the rig.
- Capes, loose armour plates and long hair are likely weak under any auto-rigger **(inference)**: bind them separately in Blender (rigid parent to a bone, or hand-weight). For pre-rendered 64–128 px sprites, minor weight artefacts rarely show: only fix what the iso camera sees **(inference)**.
- No independent test of Tripo rig quality exists. Test 2–3 real models before committing the cast.

### 6.2 Retargeting presets via Tripo

`animations` takes up to 5 per call at 10 credits each. For a game-feel set on a v3.0/v2.5 rig, order: `idle`, `walk`, `run`, `slash`, `hurt`, then add `jump`, `shoot`, `fall` as needed. Use `animate_in_place: true` for locomotion: the pre-render pipeline needs no root motion, and Godot/sim movement comes from code. If the flag is ignored, strip root translation in Blender.

### 6.3 Extra clips from free libraries

Tripo's basic set is small. Everything else comes from free libraries retargeted onto the Mixamo-spec rig in Blender:

- **Mixamo** (Adobe, free): large humanoid library including a dying clip. Upload route (send the Tripo mesh to Mixamo) is a second option, but re-uploading after weight edits in Blender is a known pain point.
- **Quaternius Universal Animation Library** (CC0, 120+ clips on a universal humanoid rig; the Standard tier is free, the Source tier with the Blender file is paid): v2.0 (2026-01-23) changed rig naming and moved Unreal export from FBX to GLB for better retargeting. Compatible with Mixamo-style rigs. Whether it contains death and attack clips is **unverified**.
- **Rokoko Blender add-on** (free; presets for Mixamo, UE4/UE5 mannequins) does the retarget. Auto-Rig Pro Remap (about $50) is a paid alternative that works with any armature: not needed on a tight budget.
- Mismatched rest poses (A-pose vs T-pose) are the usual cause of bad arms after a retarget: match the pose first, or apply the library's rest pose to the target before retargeting.
- Cheapest robust route **(inference)**: Tripo rig `spec=mixamo` (25 credits) → Blender → Rokoko retarget of all further clips (free). Tripo retargets (10 credits each) only for the quick basics.

### 6.4 Death animations (no Tripo preset)

In order of effort:

1. Mixamo "Dying" (or a Quaternius clip if one exists), retargeted with Rokoko.
2. Tripo `preset:biped:defeat_02` / `defeat_03` / `fall` on a v1.0 rig (not documented as death; check the look).
3. Key a short fall in Blender (pose library + NLA) **(inference)**: a sprite death needs only about 10–15 frames per direction, and the last frame is held.

Quadrupeds: no creature death preset either: key it by hand (collapse and roll) or reuse `fall`-like poses **(inference)**.

### 6.5 In-place clips

Always render in-place. A walk cycle must loop with the first and last frame equal in pose, no net translation. Use `animate_in_place` at retarget time or remove root motion in Blender (lock the hips X/Y, keep Z bob).

---

## 7. Blender pipeline for pre-rendered 8-direction sprites

Everything here is general Blender knowledge unless stated: **verify operators and property names on the installed Blender version** (the manual was not fetched). Run headless: `blender -b -P render.py -- <args>`. This is the shared Route A/B render stage: Tripo assets and primitive assets leave the same camera and lighting rig.

1. **Import** the GLB: `bpy.ops.import_scene.gltf(filepath=...)`. Prefer GLB (PBR textures embedded, Y-up, metres) over FBX (scale and axis quirks, and Godot needs a converter). If a clip is a separate GLB per animation, import all, keep one armature, and move each action to that armature; set fake users so actions survive.
2. **Actions and NLA.** The glTF importer creates one action per animation: list `bpy.data.actions`, assign with `arm.animation_data.action = act`, set `scene.frame_start/end` from `act.frame_range`. Push each action to its own NLA track if a single scene file is wanted.
3. **Normalise.** Check scale and facing after import (Tripo's GLB scale and axis are not documented: section 10). Apply transforms, put the origin at the feet, face the model toward a fixed "south".
4. **Re-material** to the project palette and lighting: Tripo's Principled BSDF is kept only for base colour. Lower metallic and roughness influence, bake or keep base colour, quantise to the project palette (post-process step or a node), and light with the **fixed project rig**: one key light from the upper left, a rim light, flat fill, no emission. Decimate modifier (collapse, ratio 0.3–0.5) only on meshes without shape keys and test the modifier order against the Armature modifier.
5. **Camera.** Orthographic, rotation X about 60° (true 2:1 dimetric is 54.736°; the kit's `world_to_screen` is 2:1, match it), Z 45°. Fix `ortho_scale` so the tallest pose of the tallest animation fits.
6. **Directions.** Parent the model to an empty and rotate the **empty** in 45° steps (8 directions). Never rotate the camera or lights, so lighting stays identical across directions.
7. **Render settings.** `scene.render.film_transparent = True`, PNG RGBA, Eevee (or Workbench with flat lighting for speed), filter size 0.5–1.0. Render at **2–4× the final cell** (for example 256–512 px for a 64–128 px result), then **downscale** (box or nearest, per the project look) and optionally palette-reduce. Outline via Freestyle or an inverted-hull shell if readability needs it. Shadows: prefer a blob-shadow sprite in the engine (consistent and simple) over a shadow-catcher pass.
8. **Frame rate.** 8–12 fps for the Diablo-2 feel; the sim runs 30 ticks per second, so 10 fps is every third tick. Every animation must share the frame count rule of its own cycle, and every animation must have the same direction count (a requirement of the directional-sprite helpers).
9. **Pack.** Rows = directions (8), columns = frames. Name loose frames `<char>_<anim>_<dir>_<frame>.png`, pack with Pillow (no TexturePacker needed) to `<char>_<anim>.png` plus a **JSON sidecar** (cell size, rows/columns, directions order, fps, loop flag, anchor).
10. **Godot 4.** Build `SpriteFrames` from the JSON in a script. Animation names are `<anim>_<dir>` (for example `walk_ne`); the direction is chosen in code with `round(angle / (TAU / 8))`, mapped through the iso projection. The Godot "Blender Spritesheet Import Plugin" (MIT, v0.0.1, very early) does something similar; a paid "8 Directions Render" Blender add-on exists. A Pillow script is simpler and under our control.

Sketch (not tested; adapt names):

```python
import bpy, math, sys, json
glb, out, size, directions = sys.argv[sys.argv.index("--") + 1:][:4]  # paths and ints from the caller
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
root = bpy.data.objects.new("pivot", None); bpy.context.scene.collection.objects.link(root)
for o in bpy.data.objects:                     # parent top-level objects under the pivot
    if o.parent is None and o is not root: o.parent = root
sc = bpy.context.scene
sc.render.film_transparent = True
sc.render.resolution_x = sc.render.resolution_y = int(size) * 4   # supersample, downscale later
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
cam.data.type = "ORTHO"; cam.data.ortho_scale = 2.4
cam.rotation_euler = (math.radians(60), 0, math.radians(45)); cam.location = (6, -6, 6)
sc.camera = cam
for act in bpy.data.actions:
    arm.animation_data.action = act
    sc.frame_start, sc.frame_end = map(int, act.frame_range)
    for d in range(int(directions)):
        root.rotation_euler.z = math.radians(45 * d)
        sc.render.filepath = f"{out}/{act.name}_{d}_"
        bpy.ops.render.render(animation=True)   # frames end up as <name>_<d>_0001.png ...
```

**Direct GLB use in real-time engines.** If a model is used in 3D (not pre-rendered), Godot 4 imports GLB natively with animations in an `AnimationPlayer` library; the Tripo Godot plugin (4.4+, text and image tasks) can generate inside the editor, but scripted API calls are reproducible and loggable, so prefer them **(inference)**. Real-time use needs the lower face budgets in 5.4 and an in-engine material pass.

**Visible gear (paper-doll layers).** If equipment should change the character's look, do not generate one model per gear combination. Generate a plain base body (rig it as above) and each gear piece separately (helmet, armour tier, weapon type, shield, cloak) from its own reference image. In Blender, bind armour and cloaks to the base armature (Armature modifier with automatic weights, then fix weights at the shoulders and hips), and parent rigid pieces (helmets, weapons, shields) to a bone. Render each layer on its own, with the same camera, clips and frames, with the other layers set to holdout so occlusion stays correct, and stack the layers in the engine in a fixed draw order per direction. Keep it affordable with a few visual tiers per slot plus own models for uniques; tint team or house colours with a mask instead of extra renders **(inference: standard practice for pre-rendered ARPGs, not a Tripo feature)**.

---

## 8. Other tools around Tripo

**Required**

| Tool | Role | Notes |
| --- | --- | --- |
| Image model via NanoGPT (Nano Banana, GPT Image) | Reference sheets and cleanup edits | Section 5.2 |
| Blender (headless `bpy`) | Clean-up, re-material, render, pack | Section 7 |
| Mixamo + Quaternius UAL (CC0) | Extra animation clips | Section 6.3 |
| Rokoko Blender add-on (free) | Retargeting clips onto the Mixamo-spec rig | |
| Poly Haven / ambientCG (CC0) | Texture and HDRI sources for the Blender re-material | Only if surfaces are re-textured procedurally or photo-based |

**Optional**

- Scenario: a Tripo reseller with a trained **style model** for keeping the concept stage consistent across a cast; costs extra, only worth it when a cast drifts.
- Meshy retexture: if Tripo's texture of one asset is poor and Meshy's retexture is better; extra account and licence to track.
- Tripo `mesh/segment` + `texture` with `part_names`: retexture a single part.

**Avoid**

- PixelLab for non-pixel-art styles; it is a pixel-art tool (`PIXELLAB-API.md`).
- Substance on a tight budget; Blender re-material plus CC0 textures does the job.
- **Synty and KitBash3D assets as Tripo inputs or training material:** their licences forbid use with AI tools.
- **Hunyuan3D open weights in the EU:** the licence excludes the EU; the API (via fal) is fine.
- Free-plan Tripo output for shipped assets (section 2).
- Auto-Rig Pro and similar paid add-ons while Rokoko is enough.

---

## 9. Recommended end-to-end recipe

1. Get the reference approved (front view) with the image model; generate left/back/right edits; clean backgrounds (section 5.2). Save under `art/refs/<asset>/`.
2. Check the balance (`GET /v3/account/balance`) and the pricing page; set a credit ceiling per asset in the script.
3. Upload views (`/v3/files`) and run a **draft**: `image-to-model` or `multiview-to-model`, H series, texture off or `fast`. Review silhouette. Iterate on the reference, not the settings.
4. Final generation with fixed seeds: hero: `v3.1-20260211` multiview, `detailed` texture, PBR, delight, `smart_low_poly`; secondary and props: single image or P2 (table in 5.4). Download the GLB immediately.
5. (Optional) Blender clean-up of joints, hands, face; export; `models/import` back to Tripo for rigging.
6. **Rig-check** (free). Fix issues. Then rig: humanoid `v3.0-20260909` + `biped` + `spec: mixamo`; creature `v2.5-20260210` + the rig-check's `rig_type`.
7. Retarget the Tripo basics in place (`idle`, `walk`, `run`, `slash`, `hurt`: 5 per call, 50 credits).
8. In Blender: import everything, retarget Mixamo/Quaternius clips with Rokoko (death, extra attacks, cast), remove root motion.
9. Re-material to the project palette and lighting rig; render 8 directions per clip with the fixed iso camera at 2–4× size; downscale; palette-clean.
10. Pack sheets plus JSON sidecar; load in Godot as `SpriteFrames` with `<anim>_<dir>` names; compare a render against the approved reference (the kit's reference gate).
11. Log in the asset manifest: model strings, seeds, task ids, credits, plan type (paid), licence note.

**Cost example, one finished animated humanoid (hero, sprites)** at 2026-11 prices:

| Step | Credits |
| --- | --- |
| Draft image-to-model, no texture (2 tries) | 40 |
| Final multiview H3.1, standard texture | 30 |
| Add-ons: HD texture +10, smart low-poly +10 | 20 |
| Rig-check | 0 |
| Auto-rig | 25 |
| 5 Tripo preset retargets | 50 |
| Mixamo/Quaternius extras via Rokoko | 0 |
| **Total** | **about 165 credits, about $1.65** |

With P2 textured (110–130) instead of H3.1, the total is about 245–265 credits. Add the reference-image calls (NanoGPT, a few cents each) and 1–2 redo rounds: budget **$2–4 per hero**, **$1–2 per secondary character**, **$0.30–1 per prop** **(inference from the price table)**.

---

## 10. Gaps and things to verify on first live use

Run one cheap end-to-end test (prop → humanoid → rig → one retarget) and record the answers here and in `docs/ROADMAP.md`.

- **Preset id format:** `preset:walk` or `walk`; `preset:biped:walk` on v1.0.
- **Web vs API credits:** separate pools? Which plan prices are real (official page returned 403)?
- **Refine / stylize:** docs and SDK disagree: confirm the endpoints return 404/2002.
- **Death preset:** does one exist on v3.0? Which clips does Quaternius UAL contain?
- **Rig-check response schema** and the exact bone lists of `tripo` vs `mixamo` spec.
- **GLB scale and axis** of generation and rig outputs; whether `animate_in_place` is honoured; whether batched retargets return one file or several.
- **Output URL expiry:** 5 minutes vs unspecified.
- **File token lifetime** and numeric rate limits: not published.
- P1 price, P-series text/multiview parameters, `mesh/complete` modes and `image-to-splat`/`depth` parameters were not read.
- Rig quality with armour, capes and quadrupeds is untested.
- Blender API calls in section 7 are unverified recall: check against the installed version.
- Free vs paid terms in practice: confirm with Tripo before a commercial release.

## Sources

- Tripo developer docs: [quick start](https://developers.tripo3d.ai/en/docs/quick-start) · [task query](https://developers.tripo3d.ai/en/docs/task-query) · [task lifecycle](https://developers.tripo3d.ai/en/docs/task-lifecycle) · [billing](https://developers.tripo3d.ai/en/docs/billing) · [files](https://developers.tripo3d.ai/en/docs/files) · [rate limits](https://developers.tripo3d.ai/en/docs/rate-limits) · [error handling](https://developers.tripo3d.ai/en/docs/error-handling) · [webhooks](https://developers.tripo3d.ai/en/docs/webhooks) · [migration v2 to v3](https://developers.tripo3d.ai/en/docs/migration-v2-to-v3) · [models and versions](https://developers.tripo3d.ai/en/docs/models-and-versions) · [texture](https://developers.tripo3d.ai/en/docs/models-texture) · [convert](https://developers.tripo3d.ai/en/docs/models-convert) · [import](https://developers.tripo3d.ai/en/docs/models-import) · [decimate](https://developers.tripo3d.ai/en/docs/mesh-decimate) · [segment](https://developers.tripo3d.ai/en/docs/mesh-segment) · [rig](https://developers.tripo3d.ai/en/docs/animations-rig) · [retarget](https://developers.tripo3d.ai/en/docs/animations-retarget) · [plugins](https://developers.tripo3d.ai/en/docs/plugins) · [changelog](https://developers.tripo3d.ai/en/docs/changelog) · [terms](https://developers.tripo3d.ai/en/terms) · [pricing](https://developers.tripo3d.ai/en/pricing)
- [Tripo Python SDK](https://github.com/VAST-AI-Research/tripo-python-sdk) (`client.py`, `models.py`) · [Tripo Godot plugin](https://cdn-web.tripo3d.ai/plugin/tripo-godot.zip) · [tripo-mcp](https://github.com/VAST-AI-Research/tripo-mcp)
- Quality and workflow (reseller and vendor, treat as claims): [Scenario Tripo guide](https://www.scenario.com/blog/tripo-image-to-3d-model-ai-2026) · [Scenario Tripo Family guide](https://help.scenario.com/articles/4692888910-tripo-family-the-complete-guide) · [Scenario image-to-3D best practices](https://help.scenario.com/en/articles/image-to-3d-best-practices/) · [Tripo DCC Bridge](https://www.tripo3d.ai/blog/tripo-dcc-bridge-for-blender)
- Animation: [Quaternius Universal Animation Library](https://quaternius.itch.io/universal-animation-library) · [Mixamo](https://www.mixamo.com) · [Rokoko Blender add-on](https://www.rokoko.com/integrations/blender)
- Sprites: [OpenGameArt 8-direction thread](https://opengameart.org/node/18092) · [Blender Spritesheet Import plugin](https://github.com/oddmode-studio/BlenderSpriteSheetImporter) · [Godot SpriteFrames docs](https://docs.godotengine.org/en/stable/tutorials/2d/2d_sprite_animation.html)
- Kit: `AI-ASSET-WORKFLOW.md` (Route B, "3D generation") · `PIXELLAB-API.md` · [Poly Haven](https://polyhaven.com) · [ambientCG](https://ambientcg.com)
