# 000 — Stack

Chosen from GAME-STACK.md (gamedev-kit). Decisions here are final unless the human reopens them.

## Game

- Working title: <title>
- Pitch: <one line>
- Closest stack recipe: <row from "Stack recipes by game type", or "none">
- 2D / 3D: <…>
- Target platforms: <web | Steam | both>
- Input: <mouse + keyboard | controller | touch>
- Language of in-game content and docs: <English>

## Stack (one choice per layer)

| Layer | Choice | Why (if not the default) |
| --- | --- | --- |
| Renderer | <Phaser / PixiJS / Three.js> | |
| Entity model | <plain objects + systems> | |
| Physics | <none / custom / Rapier> | |
| UI | <DOM overlay> | |
| Levels | <LDtk / Tiled / procedural / JSON> | |
| Desktop / Steam | <Electron + steamworks.js> | |

## Art and audio

- Reference route: <gemini | openai | nanogpt>, main reference model <gemini-nano-banana-2.1 | gpt-image-2.5-flare>
- Build routes in use: <A Blender from primitives / B image-to-3D + Blender / C code-built UI / direct images>
- Base resolution or polygon budget: <e.g. 640×360 integer-scaled / 3k tris per unit>
- Generation budget: <USD per day>, ask before any run above <USD>
- Audio direction: <code SFX / ElevenLabs / Suno hero tracks / voice yes-no>

## Pinned versions

- Node <version>, Python <version>, Blender <version>

## Performance budgets

See `perf/budgets.json`.

## Decisions

- <YYYY-MM-DD> — <decision> — <reason>
