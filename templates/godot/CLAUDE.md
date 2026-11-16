# <Game name> — rules for agents

## Before you start (every session)
Read the gamedev-kit brief `docs/START-HERE.md` from the plugin first; the kit's SessionStart hook gives the path, or run `/gamedev-kit:briefing`. Then read `docs/STATUS.md`: where the project stands and what is next. Before a new asset group, a new major system or a stack change, re-read the full kit documents it lists. Everything in this project is in English: replies, code, docs, in-game text and all prompts for AI tools.

End every session with `/gamedev-kit:handoff`: checks run, `docs/STATUS.md` updated and committed.

Stack and principles: GAME-STACK.md and GODOT.md (gamedev-kit knowledge). Chosen stack: docs/specs/000-stack.md. Concept: docs/concept.md.

Godot: <version>, console executable: <path>. Below, `<godot>` means that executable.

This project uses the `gamedev-kit` Claude Code plugin. Its skills hold the shared knowledge: `gamedev-kit:game-stack`, `gamedev-kit:asset-workflow`, `gamedev-kit:nanogpt-api`, `gamedev-kit:pixellab-api`, `gamedev-kit:tripo-api`, `gamedev-kit:asset-forge`, `gamedev-kit:godot`, `gamedev-kit:indie-guide`, `gamedev-kit:story-design`, `gamedev-kit:game-feel`, and the workflows `/gamedev-kit:briefing`, `/gamedev-kit:new-asset`, `/gamedev-kit:playtest`, `/gamedev-kit:handoff`, `/gamedev-kit:game-concept`, `/gamedev-kit:stack-advisor`, `/gamedev-kit:sync-docs`. Load the matching skill before planning, building assets or answering design questions. Where this file or docs/specs/ disagree with the kit, this project wins.

For every task, tell the human which Claude model you recommend (Opus: coordination, specs, art direction; Sonnet: most building; Haiku: mechanical edits).

## Roles
- The human designs, picks references and playtests. Agents build. Ask the human when a design choice is not in a spec.
- Decisions recorded in docs/specs/* are final. Do not reopen them.

## Architecture
- sim/ is pure and deterministic: RefCounted classes only, no nodes or scenes, no global randi()/randf() (use the world's RandomNumberGenerator), no Time or OS clock. tests/test_sim_purity.gd checks this.
- Players and bots act only through sim commands.
- All content is JSON in data/, checked by a schema script at load and in the tests.
- All art and audio come from scripts in art/, audio/ and tools/ (or Asset Forge exports). Never hand-edit files in assets/, .godot/ or *.import.
- The sim contract stays: World.create(seed, config), world.step(commands), world.serialize(), World.deserialize(text) in sim/world.gd. The game layer logs every command (game/command_log.gd) for replays and bug reports.
- Write .gd, .tscn, .tres and project.godot as text; run `<godot> --headless --path . --import` after adding assets; screenshots need a normal (not headless) run.

## Feel
- Every feel value (input buffer, coyote time, hit-stop, shake, camera, UI timing) lives in data/feel.json with a range in the schema. Timing that changes outcomes is in the sim, in ticks; effects are in render/ui. See GAME-FEEL.md.
- Prove timing rules with tick tests and check effects with a filmstrip you read. The human tunes values in the dev tuning panel; do not tune by your own taste.

## Bugs and playtests
- Every sim bug: a replay in tests/fixtures/replays/ (from the F8 bug report or written by hand) that fails before the fix and passes after it. Non-sim bugs: a scripted Godot run with a screenshot, kept as a test. No test, not fixed. See PLAYTEST-AND-BUGS.md and `/gamedev-kit:playtest`.
- Playtest notes go to docs/playtests/; triage proposes, the human decides changes to rules, economy, scope and story.

## Art: reference first (default for every asset group)
- Before building any final visual asset, generate options with <Nano Banana 2.1 | GPT Image 2.5> via tools/gen_image.py (provider: <gemini | openai | nanogpt | pixellab>), show the human a contact sheet, and wait for a pick.
- Then generate reference sheets (orthographic turnarounds, UI mockups) from the pick; approved ones go to art/refs/<group>/.
- Build assets to match the references: Blender recipes in art/blender/ (Route A), image-to-3D + Blender (Route B), or HTML/SVG/Pillow for UI (Route C).
- Run `python art/py/compare.py --ref <view> --render <render> --out build/previews/<asset>_compare.png` and read the comparison before reporting done. Max 3-5 rounds, then ask the human.
- Greybox placeholders without references are allowed only before the vertical slice.

## Assets
- Follow AI-ASSET-WORKFLOW.md for which generator to use per asset type.
- Every AI image (reference or shipped) has a recipe in art/recipes/ and an entry in assets/manifest.json (provider, model, date, cost, licence); shipped assets list the references they were built from.
- Read the contact sheet, comparison or spectrogram before reporting an asset done. The human approves hero assets.
- Never print or commit API keys (GEMINI_API_KEY, OPENAI_API_KEY, NANOGPT_API_KEY, PIXELLAB_API_KEY, TRIPO_API_KEY). Ask before any generation run estimated above $<budget>.

## Working rules
- Touch only the files your task brief assigns to you.
- Work in your own git worktree and branch (agent/<task-id>). Never commit to main. Never force-push.
- Before reporting done run `<godot> --headless --path . --import`, then `<godot> --headless --path . --script res://tests/run_tests.gd` and `python tools/check_assets.py`, and paste the results. Hooks in .claude/settings.json block edits to generated folders.
- Reviews go to the agents in .claude/agents/ (reviewer, art-director, perf-auditor); they see the diff, the spec and the check results, not your reasoning.
- After changing gameplay, run the bots (headless, through the same command API) and summarise the report.
- Every exploit or bug fixed gets a regression test.
- Save format changes: bump the version, add a migration, add a fixture save.

## Pinned versions
- Godot <version>, Blender <version>, Python <version>
