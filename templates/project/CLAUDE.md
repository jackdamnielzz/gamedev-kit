# <Game name> — rules for agents

## Before you start (every session)
Read the gamedev-kit brief `docs/START-HERE.md` from the plugin first; the kit's SessionStart hook gives the path, or run `/gamedev-kit:briefing`. Before a new asset group, a new major system or a stack change, re-read the full kit documents it lists. Everything in this project is in English: replies, code, docs, in-game text and all prompts for AI tools.

Stack and principles: GAME-STACK.md (gamedev-kit knowledge). Chosen stack: docs/specs/000-stack.md. Concept: docs/concept.md.

This project uses the `gamedev-kit` Claude Code plugin. Its skills hold the shared knowledge: `gamedev-kit:game-stack`, `gamedev-kit:asset-workflow`, `gamedev-kit:nanogpt-api`, `gamedev-kit:indie-guide`, and the workflows `/gamedev-kit:new-asset`, `/gamedev-kit:game-concept`, `/gamedev-kit:stack-advisor`, `/gamedev-kit:sync-docs`. Load the matching skill before planning, building assets or answering design questions. Where this file or docs/specs/ disagree with the kit, this project wins.

For every task, tell the human which Claude model you recommend (Opus: coordination, specs, art direction; Sonnet: most building; Haiku: mechanical edits).

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
