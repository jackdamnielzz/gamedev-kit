# NanoGPT API — a complete working reference

A portable guide for an AI agent or developer who has to use NanoGPT in a project: what the service is, what it can do, every API you are likely to need, how billing works, and the practical lessons learned from using it for real. Copy this file into any project; it does not depend on anything else.

Sources: the official documentation at https://docs.nano-gpt.com (index: https://docs.nano-gpt.com/llms.txt), the live model catalogues, and hands-on use of the image API. Facts were checked on **20 October 2026**. Model IDs, prices and limits change often: always confirm them with the discovery endpoints (section 4) before relying on a number in this file.

---

## 1. What NanoGPT is

NanoGPT is a pay-as-you-go **aggregator**: one account, one balance and one API key give access to hundreds of models from many providers (OpenAI, Anthropic, Google, xAI, DeepSeek, Qwen, Moonshot, MiniMax, ByteDance, Black Forest Labs, ElevenLabs, Kling, Veo and many more).

| Capability | Main endpoint | Notes |
| --- | --- | --- |
| Text / chat (LLMs) | `POST /api/v1/chat/completions` | OpenAI-compatible; also Responses API and Anthropic Messages API |
| Images (generate, edit, image-to-image) | `POST /api/v1/images` (normalized) or `POST /v1/images/generations` (OpenAI-compatible), `POST /api/v1/images/edits` | ~250 image models incl. GPT Image 2 / 2.5, Nano Banana, Seedream, FLUX, Recraft, Qwen Image, background removers, upscalers |
| Video | `POST /api/generate-video` + `GET /api/video/status` | ~190 models: Veo 3.x, Kling, Seedance, Wan, Hailuo, Sora 2, lipsync, upscalers, extend |
| Speech (TTS) | `POST /api/v1/audio/speech` | OpenAI, ElevenLabs, Inworld, Kokoro, Gemini, Qwen, MiniMax … |
| Music | `POST /api/v1/audio/speech` with a music model | ElevenLabs Music, Minimax Music, Lyria, ACE-Step … |
| Sound effects | `POST /api/v1/audio/speech` with a sound-effects model | e.g. `elevenlabs/sound-effects/v2` |
| Speech-to-text | `POST /api/v1/audio/transcriptions` (OpenAI-compatible) or `POST /api/transcribe` | Whisper, gpt-4o-mini-transcribe, ElevenLabs STT (diarization) |
| Embeddings | `POST /api/v1/embeddings` | OpenAI, BGE, Qwen3, Gemini embeddings |
| Web search / scraping | `:online` model suffix, `POST /api/web`, `POST /api/scrape-urls` | Linkup, Tavily, Exa, Brave, Kagi, Perplexity, Firecrawl … |
| Batch jobs | `POST /api/v1/batches` | Cheaper async chat/responses jobs, 24 h window |
| Extras | memory, PII redaction, moderation, BYOK, MCP server, TEE models | see sections 12–14 |

Billing is per request from a prepaid balance (USD or the Nano cryptocurrency), with no minimum fee per request and no deposit fee. There is also an optional subscription that covers many open-source text models within token quotas.

---

## 2. Hosts, base URLs and authentication

### Hosts

| Use | Base URL |
| --- | --- |
| **All API-key requests (recommended)** | `https://api.nano-gpt.com` — larger request bodies and longer runtimes |
| Website, dashboard, key management, OAuth, Management API | `https://nano-gpt.com` |

Paths are identical on both hosts (`https://api.nano-gpt.com/api/v1/chat/completions` = `https://nano-gpt.com/api/v1/chat/completions`), but the model catalogues can differ during rollouts: discover models on the host you call.

| Client | Base URL to configure |
| --- | --- |
| OpenAI SDK (Python/JS) | `https://api.nano-gpt.com/api/v1` |
| Anthropic SDK | `https://api.nano-gpt.com/api` (the SDK appends `/v1/messages`) |
| Raw chat / responses / messages | `https://api.nano-gpt.com/api/v1/{chat/completions, responses, messages}` |
| OpenAI-compatible image generation | `https://api.nano-gpt.com/v1/images/generations` (note: no `/api`) |

Authenticated JSON bodies for chat/responses/messages may be up to **32 MiB**; image/video uploads in JSON should stay **≤ 4 MB** per file (host larger media and pass a URL where the endpoint allows it).

### Authentication

- Key format: `sk-nano-<uuid>` (old accounts may have a plain UUID; both work). Create keys at https://nano-gpt.com/api.
- Send it as `Authorization: Bearer <key>` (recommended) or `x-api-key: <key>`.
- Model/catalogue listing endpoints work **without** a key.
- Per-key options in the dashboard: requests-per-day and USD-per-day caps (reset 00:00 UTC), allowed browser origins.
- Management tokens (`sk-nano-mgmt-…`) only work on `/api/management/v1` (usage monitoring, key administration); they cannot run models.

### Key safety (for agents)

- Read the key from an environment variable, conventionally `NANOGPT_API_KEY`. Never print, log, echo, commit or write it into a repository file. Never put it in client-side code.
- On Windows a user-level variable set with `[Environment]::SetEnvironmentVariable('NANOGPT_API_KEY', '…', 'User')` is invisible to already-running processes until they restart; a script can read it directly from the registry (`HKCU\Environment`) as a fallback.
- Use a separate key per project, with a USD/day cap, so a bug cannot drain the balance.

---

## 3. Money: balance, prices, usage

| Need | Call |
| --- | --- |
| Current balance | `POST https://api.nano-gpt.com/api/check-balance` → `{ "usd_balance": "12.34", "nano_balance": "…", "nanoDepositAddress": "nano_…" }` |
| Aggregate spend per day/model | `GET /api/v1/usage?from=YYYY-MM-DD&to=YYYY-MM-DD&group_by=day,model` (last 30 UTC days by default) |
| Cost of one recent request | Request Billing endpoint with the response's `X-Request-ID` (within 24 h) |
| Subscription quota | `GET /api/subscription/v1/usage` |
| Price of a model | the discovery endpoints in section 4 (`pricing`, `effective_pricing`, `public_pricing`) or https://nano-gpt.com/pricing |

Many generation responses also return `cost`, `paymentSource` and `remainingBalance` in the body: log them.

**Important pricing lessons (verified by real bills):**

- **Listed media prices can be for the default quality, not the one you ask for.** NanoGPT's public price list for `gpt-image-2` (e.g. $0.066 for 1024×1024) matched what we were billed at `quality: "medium"`; `quality: "high"` was billed about **2.4×** that ($0.156–0.165 for 1024×1024, $0.133 for 1536×1024, $0.17–0.19 for 2048×1152). Always compare the `cost` returned by the first real call with your estimate, and calibrate your budget logic on actual costs.
- Text models are priced per million input/output tokens; media models per image, per second, per video, per 1,000 characters (TTS) or per minute (STT), depending on the model. Read the model's pricing object rather than assuming a unit.
- Failed generations (e.g. HTTP 503) were not billed in our experience; confirm with the returned `cost`.

---

## 4. Discovering models (do this instead of hardcoding)

| Catalogue | Endpoint (no key needed) |
| --- | --- |
| Text models | `GET /api/v1/models` (minimal, OpenAI shape) · `GET /api/v1/models?detailed=true` (context length, max output, capabilities, `pricing` per million tokens, `supported_service_tiers`, `supported_batch_endpoints`) |
| Image models (normalized API) | `GET /api/v1/images/models` → each model has `supported_parameters`, `capabilities`, and an `endpoints` URL |
| Image model pricing + limits | `GET /api/v1/images/models/{modelId}/endpoints` (use the `endpoints` URL from the list; IDs contain slashes) → `pricing`, `public_pricing.per_image`, `input_reference_constraints` |
| Image models (legacy list) | `GET /api/v1/image-models?detailed=true` |
| Video models | `GET /api/v1/video-models?detailed=true` |
| Audio models (TTS, STT, music, sound effects) | `GET /api/v1/audio-models?detailed=true&type=all|tts|stt` |
| Embedding models | `GET /api/v1/embedding-models` |
| Providers for one open-source text model | `GET /api/models/{canonicalId}/providers` |

Treat new fields as additive, cache the catalogues briefly (they are cacheable), and refresh them: availability and capabilities change.

### Example model IDs (snapshot, 20 Oct 2026)

- Text: `openai/gpt-6.1-sol`, `openai/gpt-latest`, `anthropic/claude-opus-5.5`, `anthropic/claude-sonnet-5.5`, `google/gemini-3.1-pro-preview`, `google/gemini-flash-latest`, `x-ai/grok-latest`, `deepseek/deepseek-latest`, `moonshotai/kimi-k3`, `z-ai/glm-5.3`, `qwen/qwen3.8-max`, `minimax/minimax-m3`.
- Image: `gpt-image-2`, `openai/gpt-image-2.5/flare/text-to-image` (+ `/edit`), `openai/gpt-image-2.5/sunburst/...`, `nano-banana-pro`, `nano-banana-2`, `bytedance/seedream-v5.0-pro`, `flux-2-pro`, `recraft-ai/recraft-v4.1/text-to-image`, `qwen-image-2.1/text-to-image`; background removal `birefnet/v2` (~$0.01), `bria/remove-background-guided` (~$0.03), `background-remover` (~$0.05).
- Video: `veo3-1-video`, `veo3-1-fast-video`, `veo3-1-lite-video`, `kling-v26-pro`, `kling-v26-std`, `bytedance/seedance-2.5`, `alibaba/wan-3.0-prime`, `minimax-hailuo-23-standard`, `sora-2`, `video-upscaler`.
- Audio: TTS `gpt-4o-mini-tts`, `tts-1`, `tts-1-hd`, `elevenlabs/eleven-v4`, `elevenlabs/eleven-v4-turbo`, `inworld-tts-1.5-max`; music `elevenlabs/music/v2.5`, `Minimax-Music-2.6`, `google/lyria-3-pro/music`, `ACE-Step-1.5`; sound effects `elevenlabs/sound-effects/v2` (~$0.002 per second); STT `whisper-1`, `Whisper-Large-V3`, `gpt-4o-mini-transcribe`, `Elevenlabs-STT`.
- Embeddings: `text-embedding-3-small` ($0.02 / M tokens), `text-embedding-3-large`, `BAAI/bge-m3`, `Qwen/Qwen3-Embedding-8B`, `gemini-embedding-001`.

---

## 5. Text generation

### 5.1 Chat Completions (OpenAI-compatible)

`POST https://api.nano-gpt.com/api/v1/chat/completions`

```python
from openai import OpenAI
import os

client = OpenAI(base_url="https://api.nano-gpt.com/api/v1", api_key=os.environ["NANOGPT_API_KEY"])
resp = client.chat.completions.create(
    model="anthropic/claude-sonnet-5.5",
    messages=[{"role": "system", "content": "You are concise."},
              {"role": "user", "content": "Explain SSE in one sentence."}],
    max_tokens=300,
)
print(resp.choices[0].message.content, resp.usage)
```

Supported (model permitting): `stream` (SSE, `data: {...}` lines ending with `data: [DONE]`), `temperature`, `top_p`, `max_tokens`, `stop`, penalties, `seed`, `logit_bias`, `n`, `tools` / `tool_choice` / `parallel_tool_calls` (OpenAI function calling; tool spec ≤ 200 KB), `response_format` (`json_object` or `json_schema` with `strict: true` — all properties required, `additionalProperties: false`), image input (`{"type":"image_url","image_url":{"url":"https://… or data:image/png;base64,…"}}`, png/jpeg/webp), video input on video-capable models, `reasoning_effort` (`none|minimal|low|medium|high|xhigh|max`), `reasoning: {"exclude": true}` to hide reasoning, `service_tier` (`flex`, `fast`/`priority` where `supported_service_tiers` lists it), `provider` routing object.

Reasoning output arrives in `choices[0].delta.reasoning` / `message.reasoning`. For clients that expect other field names: `/api/v1legacy/chat/completions` (uses `reasoning_content`) and `/api/v1thinking/chat/completions` (reasoning folded into `content`).

### 5.2 Other text APIs

| API | Endpoint | When |
| --- | --- | --- |
| Responses (OpenAI) | `POST /api/v1/responses` | Stateful threads (`previous_response_id`), background jobs, Responses-style events |
| Messages (Anthropic) | `POST /api/v1/messages` | Use the Anthropic SDK unchanged (base URL `https://api.nano-gpt.com/api`); works for non-Anthropic models too; tools, vision, PDFs, thinking, caching |
| Legacy completions | `POST /api/v1/completions` | Best effort only |
| Batch | `POST /api/v1/batches` (file-backed JSONL) or `https://api.nano-gpt.com/api/beta` (inline) | Many offline requests, cheaper tokens, 24 h window, one model and one endpoint per batch |

### 5.3 Model suffixes (append to the model ID)

| Suffix | Effect |
| --- | --- |
| `:online`, `:online/linkup-deep`, `:online/exa-instant`, `:online/brave`, `:online/native`, … | Web search before answering (standard ≈ $0.006, deep ≈ $0.06 per request, plus tokens) |
| `:memory`, `:memory-<days>` | Context Memory: unlimited-length conversations, retention 1–365 days |
| `:reasoning-effort/high` (`none|low|medium|high|xhigh|max`) | Default reasoning effort for clients without a setting |
| `:reasoning-exclude` | Hide reasoning output |
| `:thinking` | Model-specific thinking variant, only where that ID exists |
| `:fast`/`:speed`, `:cheap`/`:price`, `:throughput`, `:latency`, `:tools`, `:caching` | Provider routing for open-source models (billed as explicit provider selection) |
| `:redaction` | PII redaction |

Suffixes compose (e.g. `openai/gpt-6.1-sol:online:memory-30`) but routing suffixes must not be combined with each other, with `X-Provider` or with a body `provider`.

### 5.4 Prompt caching

Implicit caching is automatic on providers that support it. `caching: true` (or `:caching`) routes to a cache-capable provider. For Claude-style explicit caching use `cache_control: {"type":"ephemeral","ttl":"5m"|"1h"}` on content blocks or the `prompt_caching: {enabled, ttl, cut_after_message_index, stickyProvider}` helper. Check `usage.prompt_tokens_details.cached_tokens`.

---

## 6. Images

### 6.1 Normalized Image API (recommended for new code)

`POST https://api.nano-gpt.com/api/v1/images` (JSON only)

```json
{
  "model": "gpt-image-2",
  "prompt": "…",
  "n": 1,
  "resolution": "2048x1152",
  "quality": "high",
  "output_format": "png",
  "input_references": ["data:image/png;base64,…", "https://example.com/ref.png"]
}
```

- `resolution` / `aspect_ratio` / `quality` / `n` / `seed` / `output_format` are model-specific: read the model's `supported_parameters` first (some models use `resolution: "1k"|"2k"|"4k"` plus `aspect_ratio`, others exact sizes).
- `input_references`: array of data URLs, public URLs or `{type:"image_url", image_url:{url}}` objects. Do not mix with legacy fields (`imageDataUrl`, `imageDataUrls`) in the same request (`conflicting_image_inputs`).
- Response: `data[i].b64_json` or `data[i].url` (signed URLs expire after about an hour: download immediately), plus `cost` and `remainingBalance`.
- No streaming; no provider selection on this route.

### 6.2 OpenAI-compatible routes

- `POST https://api.nano-gpt.com/v1/images/generations`: `model`, `prompt`, `n`, `size`, `response_format` (`b64_json` default or `url`), `quality`, `output_format`, `background` (GPT Image 1/1.5/2.5 only), image inputs via `imageDataUrl` / `imageDataUrls`, `maskDataUrl`, `strength`, `guidance_scale`, `num_inference_steps`, `seed`.
- `POST /api/v1/images/edits` (alias `/edit`): multipart (`image`, `image[]`, `mask`, `prompt`, `model`, `size`, `n`) or JSON. GPT Image 2 is the choice for masked edits; `openai/gpt-image-2.5/flare/edit` for natural-language edits.

### 6.3 GPT Image 2 on NanoGPT (verified facts)

| Fact | Detail |
| --- | --- |
| Model ID | `gpt-image-2` (successors: `openai/gpt-image-2.5/flare/...`, `/sunburst/...`) |
| Sizes | Fixed list only: 1024x1024, 1024x768, 1536x1024, 1024x1536, 1152x2048, 2048x1152, 2560x1440 (no 3:1, no free sizes — unlike OpenAI's own API) |
| Quality | `low`, `medium`, `high`; high costs ≈ 2.4× the listed price (section 3) |
| Variants | `n` up to 4 |
| Reference images | up to **4** per request on NanoGPT (`max_input_images`), png/jpeg/webp |
| Transparency | `background` is **not** supported for gpt-image-2: generate on a flat colour (e.g. magenta #FF00FF) and key it out yourself, or run a background remover model |
| Reference size | A 3.7 MB 2048-px PNG reference failed with `400 INVALID_IMAGE_INPUT` ("Unable to safely load the image"); ~1 MB 1024-px PNGs worked. Downscale references to ≤ 1024 px / ≤ 1.5 MB |
| Transient errors | `503 rate_limiter_unavailable` ("Image request protection is temporarily unavailable") happens now and then, is not billed, and succeeds on retry after 20–60 s |
| Consistency | No memory between calls and no fine-tuning: attach the approved reference image and repeat the full description in every prompt |

---

## 7. Video

1. Submit: `POST https://api.nano-gpt.com/api/generate-video`

```json
{ "model": "veo3-1-fast-video", "prompt": "…", "duration": "8", "aspect_ratio": "16:9", "resolution": "720p" }
```

Optional, per model: `imageDataUrl` / `imageUrl` (image-to-video, ≤ 4 MB inline), `videoUrl` / `videoDataUrl` (extend/edit/upscale), `referenceImages`, `generateAudio`, `negative_prompt`, `seed`, `mode` (`text-to-video|image-to-video|reference-to-video|video-edit`), audio inputs for lipsync models.

2. The response is `202` with `{ "runId": "vid_…", "status": "pending", "cost": <precharge>, "remainingBalance": … }`.
3. Poll `GET https://api.nano-gpt.com/api/video/status?requestId=<runId>` every ~5 s until `data.status` is `COMPLETED` (video at `data.output.video.url`; download it) or `FAILED`. Final `cost` comes with `COMPLETED`.

Pricing differs per model (per video, per second, by resolution, with/without audio). Example snapshot: `veo3-1-lite-video` $0.05/s at 720p, `kling-v26-std` $0.25 per 5 s, `veo3-video` $3.20 per 8 s without audio.

---

## 8. Audio

### 8.1 Text-to-speech

`POST https://api.nano-gpt.com/api/v1/audio/speech` → raw audio bytes (`Content-Type` tells the format).

```json
{ "model": "gpt-4o-mini-tts", "input": "Hello!", "voice": "alloy", "response_format": "mp3", "speed": 1, "instructions": "warm, slow", "stream": false }
```

`stream: true` gives chunked audio on OpenAI and ElevenLabs TTS models; others return a buffered file. Voices and formats differ per model: read `supported_parameters` from the audio catalogue. Voice cloning exists (`qwen-voice-clone`, `minimax-voice-clone`, async).

### 8.2 Music and sound effects

Same endpoint. With a music or sound-effects model, `input` is the description and `voice` is ignored (pass any string if your SDK requires it):

```json
{ "model": "elevenlabs/music/v2.5", "input": "Dirty garage rock for a junkyard robot fight, 140 BPM, distorted guitars, loopable" }
```

Durations are model-specific (often 10–30 s by default). Prefer models with flat or per-second pricing when cost predictability matters. Check licence/commercial-use terms of the underlying provider before shipping generated music in a commercial product.

### 8.3 Speech-to-text

- OpenAI-compatible: `POST /api/v1/audio/transcriptions` (multipart, `file`, `model`).
- Native: `POST https://api.nano-gpt.com/api/transcribe` with multipart `audio` (≤ 3 MB) or JSON `{"audioUrl": "...", "model": "...", "language": "auto"}`; `Elevenlabs-STT` adds `diarize` and runs async (poll the status endpoint). YouTube transcription and video transcription models exist.

---

## 9. Embeddings

`POST https://api.nano-gpt.com/api/v1/embeddings` — exactly the OpenAI shape (`model`, `input` string or array, optional `dimensions` on models that support reduction). Works with the OpenAI SDK via the base URL in section 2.

---

## 10. Web search and scraping as tools

| Need | Endpoint |
| --- | --- |
| A model answer with live web context | `chat/completions` with a `:online…` suffix or a `web_search` body object |
| Raw search results / sourced answer / structured output with date and domain filters | `POST https://api.nano-gpt.com/api/web` (`query`, `provider`: linkup, tavily, exa, kagi, perplexity, valyu, brave, sofya, firecrawl; `depth`; `outputType`: `searchResults|sourcedAnswer|structured`) — also at `POST /api/v1/data/web/search` |
| Page content as markdown | `POST https://api.nano-gpt.com/api/scrape-urls` with `{"urls": [... up to 5], "stealthMode": false}` → `results[].markdown` (also `/api/v1/data/url/scrape`) |

---

## 11. Limits, errors and retries

- Throughput: **25 requests per second** per account (contact support for more). Optional per-key RPD and USD/day caps return `429` with `code: daily_rpd_limit_exceeded | daily_usd_limit_exceeded` and a `Retry-After` header.
- Error shapes: OpenAI-style `{"error":{"message","type","code","param"}}` on most `/api/v1/*`; Anthropic-style on `/v1/messages`; older endpoints may return `{"error":"Insufficient balance","status":402}`.

| Status | Meaning | Action |
| --- | --- | --- |
| 400 | Invalid request (e.g. bad size, `INVALID_IMAGE_INPUT`, `conflicting_image_inputs`) | Fix the request; do not retry unchanged |
| 401 | Missing/invalid key | Stop; fix credentials |
| 402 | Insufficient balance | Stop and tell the owner to top up |
| 403 | Not permitted (model, origin) | Choose another model / fix key settings |
| 408, 504 | Timeout | Retry with backoff; use long client timeouts (image/video calls can take minutes) |
| 413 | Payload too large | Shrink attachments |
| 429 | Rate limited | Wait (`Retry-After`), then retry |
| 500, 503 | Server/provider busy (incl. `rate_limiter_unavailable`) | Retry with backoff: e.g. 20 s, 60 s, 120 s |

Keep the `X-Request-ID` response header for support and billing lookups.

---

## 12. Routing, privacy and extras

- **Provider selection** (open-source text models): `X-Provider: <id>` header, body `provider` (string or `{order, only, ignore, sort, max_price, allow_fallbacks, require_parameters, quantizations}`), or suffixes. Always billed pay-as-you-go at the chosen provider's price.
- **Zero data retention / TEE**: ZDR-only routing can be enabled per account/key; `TEE/…` models run in attested enclaves with verifiable signatures.
- **PII redaction** (`:redaction`), **inline moderation** (`moderation` header), **AI detection**, **NSFW image classification**: separate paid options.
- **BYOK**: store your own provider keys and route chat completions through them; NanoGPT adds a 5% platform fee.
- **Accountless x402 payments**: some endpoints can be paid per request without an account (`x-x402: true` returns a `402` quote); see the docs if you need it.

---

## 13. Using NanoGPT from AI coding tools

- **MCP server** (gives an agent LLMs, image, video, speech, music, search and scraping as tools): `npx -y @nanogpt/mcp` with `NANOGPT_API_KEY` set. Claude Code: `claude mcp add nanogpt --scope user --env NANOGPT_API_KEY=… -- npx -y @nanogpt/mcp` (on native Windows launch through `cmd /c "C:\Program Files\nodejs\npx.cmd" -y @nanogpt/mcp`).
- Any OpenAI-compatible or Anthropic-compatible tool (Cline, Roo Code, Cursor, OpenCode, Codex CLI, LibreChat, OpenWebUI, n8n …) works by setting the base URL from section 2 and the key.

---

## 14. Recommended client pattern (for an agent writing code)

1. Keep the key in `NANOGPT_API_KEY`; never print it.
2. Discover the model's parameters and price from the catalogue endpoint; validate size/quality/n/reference counts locally before sending.
3. Estimate the cost, check it against a hard per-run and per-day budget, and refuse (and ask the human) when it would exceed it. Calibrate estimates on the `cost` returned by real calls (listed prices can be too low; see section 3).
4. Dry-run mode: print the request (with attachments replaced by file names) and the estimate without sending.
5. Send with a long timeout; retry 429/503 with backoff; never retry 400/401/402 unchanged.
6. Save outputs immediately (signed URLs expire), log model, settings, prompt hash, `cost`, `remainingBalance` and `X-Request-ID` to an append-only log.
7. For creative assets, request **one** output at a time, inspect it, then decide whether to generate another: cheaper than batches of variants.

### Minimal Python image call (normalized API)

```python
import base64, json, os, urllib.request

def generate_image(prompt, model="gpt-image-2", resolution="1024x1024", quality="high", refs=()):
    body = {"model": model, "prompt": prompt, "n": 1, "resolution": resolution,
            "quality": quality, "output_format": "png"}
    if refs:
        body["input_references"] = [
            "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode() for p in refs]
    req = urllib.request.Request(
        "https://api.nano-gpt.com/api/v1/images", data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + os.environ["NANOGPT_API_KEY"]})
    with urllib.request.urlopen(req, timeout=600) as r:
        resp = json.load(r)
    item = resp["data"][0]
    if "b64_json" in item:
        png = base64.b64decode(item["b64_json"])
    else:
        png = urllib.request.urlopen(item["url"], timeout=120).read()
    return png, resp.get("cost"), resp.get("remainingBalance")
```

### Minimal TypeScript chat call

```ts
const res = await fetch("https://api.nano-gpt.com/api/v1/chat/completions", {
  method: "POST",
  headers: { "Content-Type": "application/json", Authorization: `Bearer ${process.env.NANOGPT_API_KEY}` },
  body: JSON.stringify({
    model: "openai/gpt-latest",
    messages: [{ role: "user", content: "Give me three names for a scrap robot." }],
    response_format: { type: "json_object" },
  }),
});
if (!res.ok) throw new Error(`NanoGPT ${res.status}: ${await res.text()}`);
const data = await res.json();
console.log(data.choices[0].message.content, data.usage);
```

---

## 15. Quick reference

| Task | Method + URL |
| --- | --- |
| List text models | `GET https://api.nano-gpt.com/api/v1/models?detailed=true` |
| List image / video / audio / embedding models | `GET …/api/v1/images/models`, `…/api/v1/video-models?detailed=true`, `…/api/v1/audio-models?detailed=true`, `…/api/v1/embedding-models` |
| Chat | `POST …/api/v1/chat/completions` |
| Responses | `POST …/api/v1/responses` |
| Anthropic Messages | `POST …/api/v1/messages` |
| Image (normalized) | `POST …/api/v1/images` |
| Image (OpenAI) | `POST https://api.nano-gpt.com/v1/images/generations` |
| Image edit | `POST …/api/v1/images/edits` |
| Video | `POST …/api/generate-video` → `GET …/api/video/status?requestId=` |
| TTS / music / sound effects | `POST …/api/v1/audio/speech` |
| Transcription | `POST …/api/v1/audio/transcriptions` or `POST …/api/transcribe` |
| Embeddings | `POST …/api/v1/embeddings` |
| Web search | `POST …/api/web` |
| Scrape | `POST …/api/scrape-urls` |
| Batch | `POST …/api/v1/batches` |
| Balance | `POST …/api/check-balance` |
| Usage | `GET …/api/v1/usage` |

(`…` = `https://api.nano-gpt.com`)

Full documentation: https://docs.nano-gpt.com · model pages and prices: https://nano-gpt.com/models, https://nano-gpt.com/pricing · support: support@nano-gpt.com.
