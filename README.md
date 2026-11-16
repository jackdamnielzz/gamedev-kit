# gamedev-kit

Niels's Claude Code plugin for building games with Claude Code: the stack catalogue, the reference-first AI art pipeline (Nano Banana / GPT Image references → Blender and code), the NanoGPT API reference, the indie development guide, and scaffolding for new games.

**This repo is the master copy of all game-dev documentation** (`docs/`). Copies elsewhere, such as the claude.ai "Game Dev" project, follow this repo. Change the repo first.

## What is inside

| Path | What |
| --- | --- |
| `docs/START-HERE.md` | The standing brief every session must read first: reading order, non-negotiable rules, where things are |
| `docs/GAME-STACK.md` | Stack, architecture, repo layout, workflow, CI, recipes per game type, templates |
| `docs/AI-ASSET-WORKFLOW.md` | Reference-first pipeline, generators per asset type, prices, licences, Steam AI disclosure |
| `docs/NANOGPT-API.md` | NanoGPT API reference |
| `docs/PIXELLAB-API.md` | PixelLab API reference: models, every endpoint and setting, sizes, costs, licence, pipeline use |
| `docs/TRIPO.md` | Tripo guide: API v3 reference, settings and quality practices for characters, creatures and props, rigging and animation, Blender pipeline to 8-direction sprites, costs, licence |
| `docs/GODOT.md` | Godot 4 recipe for agent-built games: when to choose it, working without the editor, pixel-art settings, 2D lights with normal maps, architecture, assets, CI and release |
| `docs/ASSET-FORGE.md` | Asset Forge, our own AI-driven 3D and pixel-art asset workshop: connecting it, its command groups, where it fits in the pipeline, when not to use it |
| `docs/indie-game-development-guide.md` | Lifecycle, design, production, marketing, release |
| `docs/STORY-AND-NARRATIVE.md` | Story without text overload: principles, case lessons, storylet engine, pacing, anti-repetition, text UX, checklist |
| `docs/GAME-FEEL.md` | Game feel: response, feedback and forgiveness, starting values per genre, where each value lives, how an agent tests feel and the human tunes it |
| `docs/PLAYTEST-AND-BUGS.md` | Playtest protocol, triage, the in-game bug report (seed + command log), replay files and regression tests |
| `skills/` | The plugin's skills (below) |
| `hooks/` | SessionStart hook that briefs every session in a game folder (below) |
| `templates/project/` | Shared files copied into every new game by `/gamedev-kit:new-game`: docs and specs, `docs/STATUS.md`, playtest template, art and audio scripts, `tools/` (`gen_image.py`, `gen_sfx.py`, `check_assets.py`, edit hooks), reviewer agents, replay fixtures |
| `templates/web/` | Engine layer for the TypeScript web stack, copied on top: a running skeleton with the sim contract, command log, F8 bug report, determinism, replay, property and data tests, ESLint rules for the sim, Playwright smoke and perf tests, CI and GitHub Pages workflows |
| `templates/godot/` | Engine layer for Godot 4, copied on top: the same skeleton in GDScript, a headless test runner, a sim purity test and CI. **Not yet run against a real Godot**: the first game that uses it checks it |
| `templates/project/tools/pixellab/` | **Pixel art only:** PixelLab scripts (character in 4/8 directions with palette snap, lint, review page and Phaser export); copied only into pixel-art games that use PixelLab. See its `README.md` and `docs/PIXELLAB-API.md` section 9.1 |

Skills (Claude loads the knowledge skills by itself when the topic comes up; the workflows you can also type):

| Skill | Type |
| --- | --- |
| `gamedev-kit:game-stack` | Knowledge: GAME-STACK.md |
| `gamedev-kit:asset-workflow` | Knowledge: AI-ASSET-WORKFLOW.md, including the push rule for the reference-first pipeline |
| `gamedev-kit:nanogpt-api` | Knowledge: NANOGPT-API.md |
| `gamedev-kit:pixellab-api` | Knowledge: PIXELLAB-API.md |
| `gamedev-kit:tripo-api` | Knowledge: TRIPO.md |
| `gamedev-kit:asset-forge` | Knowledge: ASSET-FORGE.md |
| `gamedev-kit:godot` | Knowledge: GODOT.md |
| `gamedev-kit:indie-guide` | Knowledge: indie guide |
| `gamedev-kit:story-design` | Knowledge: STORY-AND-NARRATIVE.md |
| `gamedev-kit:game-feel` | Knowledge: GAME-FEEL.md |
| `/gamedev-kit:briefing [task]` | Read the docs (all of them for a new game, the relevant parts for an existing one) and give a short brief |
| `/gamedev-kit:new-game [title]` | Scaffold a new game in the current folder |
| `/gamedev-kit:new-asset <group>` | Run the reference-first pipeline for one asset group |
| `/gamedev-kit:playtest [plan \| notes \| triage \| bug]` | Plan a playtest, write up notes, triage findings, or turn a bug report into a replay test and a fix |
| `/gamedev-kit:handoff` | End a session: run the checks, update and commit `docs/STATUS.md` |
| `/gamedev-kit:game-concept [idea]` | One-page concept in `docs/concept.md` |
| `/gamedev-kit:stack-advisor [question]` | Pick stack options, record them in `000-stack.md` |
| `/gamedev-kit:sync-docs [change]` | Put a lesson or change into this repo (only when you call it) |

## Automatic briefing in every session

When a Claude Code session starts in a game folder where the kit is enabled, the hook `hooks/session-start.js` adds a briefing to Claude's context. You don't need to type anything:

- **New game** (no `docs/specs/000-stack.md` yet): Claude must first read START-HERE, GAME-STACK, AI-ASSET-WORKFLOW, the indie guide, STORY-AND-NARRATIVE and GAME-FEEL in full, give you a short brief, and only then start, even if your first message says "start building".
- **Existing game:** Claude reads START-HERE, the project's `docs/STATUS.md`, `CLAUDE.md` and `docs/specs/`, plus the kit sections that fit the task, and re-reads everything before a new asset group or major system.
- **Resumed or compacted session:** a short reminder of the rules.

The hook needs Node on the computer, which the stack requires anyway. It runs only where the plugin is enabled, so your other projects are not affected. You can also trigger the briefing by hand with `/gamedev-kit:briefing`.

## Use it only in game folders

The kit is enabled **per game folder** (project scope), not for your whole computer. Your other software projects never see it.

### New game (easiest)

In PowerShell, from your clone of this repo:

```
.\scripts\new-game.ps1 -Name MyGame            # creates D:\Programmeren\MyGame
.\scripts\new-game.ps1 -Name MyGame -Root D:\Programmeren\Games
```

It creates the folder, runs `git init`, enables the kit for that folder only, and opens VS Code. Then start Claude Code there and run `/gamedev-kit:new-game MyGame`.

### By hand (new or existing game)

Inside the game folder:

```
claude plugin marketplace add jackdamnielzz/gamedev-kit --scope project
claude plugin install gamedev-kit@gamedev-kit --scope project
```

This writes `.claude/settings.json` in the game folder. Commit it with the game: on another computer, Claude Code reads it when you open the game folder and asks to install the kit (or run the two commands there again). Use this also to add the kit to existing games such as pins-and-ribbons.

Check: start Claude Code in the game folder and type `/gamedev-kit:` (the skills are listed). In any other folder they are not.

To remove the kit from one game: `claude plugin uninstall gamedev-kit@gamedev-kit --scope project` in that folder.

### Also needed on the computer

Git, Node 20+ (22 in the web template), Python 3.10+, Blender (the version gets pinned per game), Godot 4 for Godot games, and one image API key as a user environment variable: `GEMINI_API_KEY`, `OPENAI_API_KEY`, `NANOGPT_API_KEY` or `PIXELLAB_API_KEY`. On Windows:

```
[Environment]::SetEnvironmentVariable('GEMINI_API_KEY', '<your key>', 'User')
```

Restart VS Code afterwards so it sees the variable.

## Update the docs and the kit

1. Edit in your local clone of this repo (e.g. `D:\Programmeren\gamedev-kit`), or ask Claude: `/gamedev-kit:sync-docs <what changed>`.
2. Commit and push.
3. Update the installed plugin:

```
claude plugin marketplace update gamedev-kit
claude plugin update gamedev-kit@gamedev-kit --scope project   # inside a game folder
```

Or in a session: `/plugin` → Installed → gamedev-kit → Update now. New sessions use the new version (or run `/reload-plugins`).

4. Replace the copies in the claude.ai "Game Dev" project with the new files from `docs/`, including `START-HERE.md`.

Existing games are not changed by an update: their own `CLAUDE.md` and `docs/specs/` stay as they were, on purpose. Ask Claude in that game to adopt a specific change if you want it there.

## Test changes locally before pushing

```
claude plugin validate .
claude --plugin-dir D:\Programmeren\gamedev-kit
```

The second command starts one session with the local version loaded, without installing it.
