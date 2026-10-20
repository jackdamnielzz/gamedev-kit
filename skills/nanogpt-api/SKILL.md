---
name: nanogpt-api
description: Complete working reference for the NanoGPT API (api.nano-gpt.com) - auth, model discovery, chat, normalized image API, GPT Image and Nano Banana quirks, video, TTS, music, sound effects, transcription, embeddings, web search, billing, errors and retries, MCP server. Use when writing or debugging code that calls NanoGPT, estimating its costs, or choosing a NanoGPT model id.
when_to_use: Any NanoGPT call, key setup, cost question or error (400 INVALID_IMAGE_INPUT, 402, 429, 503 rate_limiter_unavailable).
---

# NanoGPT API

The reference lives in `${CLAUDE_PLUGIN_ROOT}/docs/NANOGPT-API.md`. Read the relevant section before writing or changing NanoGPT code.

Key reminders (details in the doc):

- Base host for API-key calls: `https://api.nano-gpt.com`. Key in `NANOGPT_API_KEY`; never print or commit it.
- Discover model ids, parameters and prices from the catalogue endpoints instead of hardcoding them; ids and prices change.
- Listed image prices can be for default quality: log the `cost` of the first real call and calibrate.
- `gpt-image-2` on NanoGPT has no `background` parameter; GPT Image 2.5 does. Keep reference images ≤ 1024 px and ≤ 1.5 MB.
- Retry 429/503 with backoff; never retry 400/401/402 unchanged.
- The NanoGPT subscription is personal and non-commercial: pay game assets from the pay-as-you-go balance.
