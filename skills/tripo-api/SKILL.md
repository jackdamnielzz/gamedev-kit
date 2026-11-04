---
name: tripo-api
description: Complete working guide to Tripo (Tripo3D) for game assets - API v3 (openapi.tripo3d.ai/v3) endpoints and parameters, model/texture/rig versions, rig types and specs, animation presets, costs in credits, limits, errors, webhooks, licence; how to get the best characters, quadrupeds and props (reference images, multi-view, settings, failure modes); rigging, retargeting extra clips, and the Blender pipeline to 8-direction pre-rendered sprites. Use when writing or debugging code that calls Tripo, choosing Tripo settings, planning image-to-3D (Route B) assets, or estimating their cost.
when_to_use: Any Tripo call, recipe, cost question or error; image-to-3D for characters, creatures or props; rigging or animating a generated model; rendering a Tripo model to sprites.
---

# Tripo

The guide lives in `${CLAUDE_PLUGIN_ROOT}/docs/TRIPO.md`. Read the relevant section before writing or changing Tripo code, recipes or asset plans.

Key reminders (details in the doc):

- API v2 was shut down on 2026-10-31. Use v3 only: base URL `https://openapi.tripo3d.ai/v3`, `Authorization: Bearer` with the key from `TRIPO_API_KEY`; never print or commit it.
- Every task type has its own endpoint; poll `GET /v3/tasks/{id}` and download outputs immediately (URLs expire quickly). Concurrency is limited per category (default 10).
- 1 credit = $0.01. Log the cost of every call and ask the human before a run above the agreed budget.
- Input is always an approved reference image (Route B), never a raw text prompt for shipped assets: single subject, clean background, even light, A-pose for characters, multi-view for heroes.
- Humanoids: rig model v3.0 with `spec: mixamo`; creatures: v2.5 with the right `rig_type` (e.g. quadruped). Run the free rig check first.
- There is no death preset: retarget a Mixamo or Quaternius (CC0) clip in Blender instead.
- Generate shipped assets on a paid plan only (you own the output); log every asset in the project's asset manifest and the Steam AI disclosure.
