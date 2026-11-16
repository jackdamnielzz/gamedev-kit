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

Before anything else, read `${CLAUDE_PLUGIN_ROOT}/docs/START-HERE.md` and then, in full and in this order: `GAME-STACK.md`, `AI-ASSET-WORKFLOW.md`, `indie-game-development-guide.md`, `STORY-AND-NARRATIVE.md` and `GAME-FEEL.md`, plus the overview of `NANOGPT-API.md` (all in `${CLAUDE_PLUGIN_ROOT}/docs/`). Skip a document only if you already read it in full earlier in this session. Give the human the short brief that START-HERE asks for, then continue.

## 1. Check the folder

- This skill runs only where the kit is enabled for the folder (project scope). Check that `.claude/settings.json` lists `gamedev-kit@gamedev-kit` under `enabledPlugins`; keep that file and commit it with the game.
- List the current folder. If it already contains a game (`package.json`, `src/`, `CLAUDE.md`), stop and ask whether to add the kit to the existing project instead of scaffolding over it. Never overwrite existing files without asking.
- Check tools: `git`, `node` (≥ 20), `python` (3.10+), `blender` (on Windows, also check `C:\Program Files\Blender Foundation\*\blender.exe`). Report what is missing with one install hint each; Blender is required for the art pipeline but not for scaffolding.
- Check which image API keys are set (only test whether `GEMINI_API_KEY`, `OPENAI_API_KEY`, `NANOGPT_API_KEY`, `PIXELLAB_API_KEY` exist; never print values).

## 2. Ask the decision questions

Read `${CLAUDE_PLUGIN_ROOT}/docs/GAME-STACK.md` (sections "Stack overview" and "Stack recipes by game type") and the "Decision checklist for a new game" in `${CLAUDE_PLUGIN_ROOT}/docs/AI-ASSET-WORKFLOW.md`. Then ask, in one round (AskUserQuestion if available), only what is not already clear from the conversation:

1. One-line pitch and genre; which stack recipe row is closest (or "none").
2. 2D or 3D; target platforms (web, Steam, both); input (mouse+keyboard, controller, touch); engine: the TypeScript web stack (default) or Godot 4 (see "When to choose Godot" in `${CLAUDE_PLUGIN_ROOT}/docs/GODOT.md`).
3. Reference route for images: Gemini direct (Nano Banana 2.1, default), OpenAI direct (GPT Image 2.5), NanoGPT, or PixelLab (pixel-art games; budget in generations). Daily generation budget in USD or generations.
4. Language of in-game content and docs (default English).

Do NOT ask the human to pick an art style here and do NOT infer one from the genre. The style is chosen in the exploration round (step 5).

## 3. Copy the templates

Copy in two layers, keeping the folder structure and including dot-folders (`.claude/`, `.github/`, `.nvmrc`). Use the Read and Write tools (works the same on Windows and Linux):

1. Everything under `${CLAUDE_PLUGIN_ROOT}/templates/project/` (shared by every game: docs, specs, STATUS, playtest template, art and audio scripts, `tools/`, reviewer agents, hooks, replay fixtures).
2. Then the engine layer on top, overwriting files with the same name: `${CLAUDE_PLUGIN_ROOT}/templates/web/` for the TypeScript web stack, or `${CLAUDE_PLUGIN_ROOT}/templates/godot/` for Godot (it brings its own `CLAUDE.md`).

Then:

- Write `gitignore.template` as `.gitignore`. Copy `tools/pixellab/` only when the game is pixel art and uses PixelLab as its art route; otherwise leave it out. Create the empty folders `art/refs/`, `audio/sfx/`, `audio/music/`, `public/assets/` (Godot: `assets/`) and `build/`.
- Merge the `hooks` block of `.claude/hooks.template.json` into `.claude/settings.json`, keeping `enabledPlugins` and anything else already there; then delete `hooks.template.json`.
- Fill in the placeholders in angle brackets in `CLAUDE.md`, `docs/concept.md`, `docs/STATUS.md`, `docs/specs/000-stack.md`, `docs/specs/art-direction.md` and, per engine, `package.json` and `index.html` (web) or `project.godot` (Godot) from the answers. Leave the style paragraph in `art-direction.md` empty until the exploration round.
- Record the chosen stack row, engine, pinned versions (Node, Python, Blender as found; Godot when chosen), reference route and budget in `000-stack.md`, each with a dated entry under Decisions.

## 4. Set up the code project

The engine layer is already a running skeleton: a placeholder deterministic sim with the kit's contract, a fixed-timestep loop, the command log, the F8 bug report, determinism, replay and (web) property and data tests, lint rules for the sim, CI and the perf guard. Do not rebuild these; build the game on top of them.

**Web:** `git init` if needed, `npm install`, then install the chosen renderer (Phaser / PixiJS / Three.js) and replace the canvas placeholder in `src/main.ts` with `src/render` and `src/ui` layers. Keep `typescript` on the pinned 6.0.x line until typescript-eslint supports a newer major. Run `npx playwright install chromium` once. Install the Python requirements from `requirements.txt` in a venv (`.venv`). Run `npm run check`, `npm run assets:check` and `npm run test:e2e`, and paste the results.

**Godot:** follow `${CLAUDE_PLUGIN_ROOT}/docs/GODOT.md`: set the pinned Godot version in `project.godot` features, `000-stack.md`, `CLAUDE.md` and `.github/workflows/ci.yml`, then run `<godot> --headless --path . --import` and `<godot> --headless --path . --script res://tests/run_tests.gd`, and take a first screenshot from a normal run. Paste the results. The Godot layer has not been run in CI yet: fix anything the first run reports and record the fix with `/gamedev-kit:sync-docs`.

Then fill in `docs/STATUS.md`: phase "prototype", what runs, next steps (the first spec, the feel gate, the first asset group).

## 5. Plan the first art exploration

Do not generate images in this skill. End by proposing the first asset groups (for example: main characters or units, one environment, the main HUD) and offer to run `/gamedev-kit:new-asset <group>` for the first one, with a cost estimate from the recipe.

## 6. Finish

Commit with message "Scaffold <title> with gamedev-kit" (including `docs/STATUS.md`). Summarise in a few lines what was set up, what is missing (tools, keys) and the next step. Tell the human that kit updates do not change this project's `CLAUDE.md`; the decisions in `docs/specs/` stay frozen on purpose.
