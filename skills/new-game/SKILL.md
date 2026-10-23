---
name: new-game
description: Scaffold a new game in the current (empty or nearly empty) folder using Niels's stack - asks the decision questions, copies CLAUDE.md, specs, art and tools templates, sets up the TypeScript/Vite project, and plans the first art exploration round.
when_to_use: The human starts a new game, says "new game", "start a game", "set up this folder for a game", or runs /gamedev-kit:new-game.
argument-hint: "[working title]"
---

# New game

Working title: $ARGUMENTS (ask if empty).

Recommended model: Opus for this whole skill (decisions here are expensive to undo). Say so to the human at the start.

## 0. Read the kit first

Before anything else, read `${CLAUDE_PLUGIN_ROOT}/docs/START-HERE.md` and then, in full: `GAME-STACK.md`, `AI-ASSET-WORKFLOW.md` and `indie-game-development-guide.md` (all in `${CLAUDE_PLUGIN_ROOT}/docs/`). Skip a document only if you already read it in full earlier in this session. Give the human the short brief that START-HERE asks for, then continue.

## 1. Check the folder

- This skill runs only where the kit is enabled for the folder (project scope). Check that `.claude/settings.json` lists `gamedev-kit@gamedev-kit` under `enabledPlugins`; keep that file and commit it with the game.
- List the current folder. If it already contains a game (`package.json`, `src/`, `CLAUDE.md`), stop and ask whether to add the kit to the existing project instead of scaffolding over it. Never overwrite existing files without asking.
- Check tools: `git`, `node` (≥ 20), `python` (3.10+), `blender` (on Windows, also check `C:\Program Files\Blender Foundation\*\blender.exe`). Report what is missing with one install hint each; Blender is required for the art pipeline but not for scaffolding.
- Check which image API keys are set (only test whether `GEMINI_API_KEY`, `OPENAI_API_KEY`, `NANOGPT_API_KEY`, `PIXELLAB_API_KEY` exist; never print values).

## 2. Ask the decision questions

Read `${CLAUDE_PLUGIN_ROOT}/docs/GAME-STACK.md` (sections "Stack overview" and "Stack recipes by game type") and the "Decision checklist for a new game" in `${CLAUDE_PLUGIN_ROOT}/docs/AI-ASSET-WORKFLOW.md`. Then ask, in one round (AskUserQuestion if available), only what is not already clear from the conversation:

1. One-line pitch and genre; which stack recipe row is closest (or "none").
2. 2D or 3D; target platforms (web, Steam, both); input (mouse+keyboard, controller, touch).
3. Reference route for images: Gemini direct (Nano Banana 2.1, default), OpenAI direct (GPT Image 2.5), NanoGPT, or PixelLab (pixel-art games; budget in generations). Daily generation budget in USD or generations.
4. Language of in-game content and docs (default English).

Do NOT ask the human to pick an art style here and do NOT infer one from the genre. The style is chosen in the exploration round (step 5).

## 3. Copy the templates

Copy everything under `${CLAUDE_PLUGIN_ROOT}/templates/project/` into the current folder, keeping the folder structure. Use the Read and Write tools (works the same on Windows and Linux). Write `gitignore.template` as `.gitignore`. Copy `tools/pixellab/` only when the game is pixel art and uses PixelLab as its art route (pixel art only); otherwise leave it out. Create the empty folders `art/refs/`, `audio/sfx/`, `audio/music/`, `public/assets/` and `build/`. Then:

- Fill in the placeholders in angle brackets in `CLAUDE.md`, `docs/concept.md`, `docs/specs/000-stack.md` and `docs/specs/art-direction.md` from the answers. Leave the style paragraph in `art-direction.md` empty until the exploration round.
- Record the chosen stack row, pinned versions (Node, Python, Blender as found), reference route and budget in `000-stack.md`, each with a dated entry under Decisions.

## 4. Set up the code project

Following GAME-STACK.md for the chosen recipe: `git init`, `npm create vite@latest . -- --template vanilla-ts` (or set up by hand if the folder is not empty), install the chosen renderer (Phaser / PixiJS / Three.js), zod, Vitest, fast-check, Playwright, ESLint + Prettier. Create the `src/sim`, `src/game`, `src/render`, `src/ui`, `src/audio`, `src/data` layers with a minimal deterministic sim, a passing unit test and a determinism test. Add the npm scripts from the "npm scripts" table that apply now (`dev`, `build`, `check`, `validate`, `refs:prepare`, `assets:compare`); leave the rest for later specs. Install the Python requirements from `requirements.txt` in a venv (`.venv`).

Run `npm run check` and paste the result.

## 5. Plan the first art exploration

Do not generate images in this skill. End by proposing the first asset groups (for example: main characters or units, one environment, the main HUD) and offer to run `/gamedev-kit:new-asset <group>` for the first one, with a cost estimate from the recipe.

## 6. Finish

Commit with message "Scaffold <title> with gamedev-kit". Summarise in a few lines what was set up, what is missing (tools, keys) and the next step. Tell the human that kit updates do not change this project's `CLAUDE.md`; the decisions in `docs/specs/` stay frozen on purpose.
