---
name: pixellab-api
description: Complete working reference for the PixelLab API (api.pixellab.ai/v2) - pixel-art models (pixen, Pro, Pro Flash, v3, PixMiniMax, pixflux, bitforge), every endpoint and its settings (images, characters with 4/8 directions, animations and templates, rotations, objects, map objects, edits, inpainting, tilesets, tiles and building kits, UI panels, pixel fonts, portraits and lip-sync, VFX, cleanup), sizes, costs in generations, plans, licence, job polling, errors, and use in the reference-first pipeline. Use when writing or debugging code that calls PixelLab, choosing a PixelLab endpoint or setting, or estimating its cost.
when_to_use: Any PixelLab call, recipe, MCP tool choice, cost question or error (402, 409, 423, 429, 529), or pixel-art generation in a project that uses PixelLab.
---

# PixelLab API

The reference lives in `${CLAUDE_PLUGIN_ROOT}/docs/PIXELLAB-API.md`. Read the relevant section before writing or changing PixelLab code or recipes.

Key reminders (details in the doc):

- Base URL `https://api.pixellab.ai/v2`, `Authorization: Bearer` with the key from `PIXELLAB_API_KEY`; never print or commit it. The same token drives the MCP server.
- Most creation endpoints are background jobs: poll `GET /background-jobs/{id}` every 5–10 s; `423` means still generating; map objects are deleted after 8 hours.
- Billing is in subscription generations; log `usage` from every response. Check `GET /balance` and `GET /pro-flash/cost` (free) before a run, and ask the human above the budget.
- Every image is `{"type": "base64", "base64": …, "format": "png"}`; sides of pixen and Pro Flash images are multiples of 4. Never rescale pixel-art references; run upscaled art through `/unzoom` first.
- Use `target_palette` with the project palette (hex) for style lock; character rotation input must face south.
- Licence: commercial use on all plans, but no training of models on the output.
- For repeatable runs use `tools/gen_image.py --provider pixellab` with a recipe; use the MCP tools for exploration in a conversation.
