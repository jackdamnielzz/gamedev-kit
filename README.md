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
| `docs/indie-game-development-guide.md` | Lifecycle, design, production, marketing, release |
| `skills/` | The plugin's skills (below) |
| `hooks/` | SessionStart hook that briefs every session in a game folder (below) |
| `templates/project/` | Files copied into every new game by `/gamedev-kit:new-game` |

Skills (Claude loads the knowledge skills by itself when the topic comes up; the workflows you can also type):

| Skill | Type |
| --- | --- |
| `gamedev-kit:game-stack` | Knowledge: GAME-STACK.md |
| `gamedev-kit:asset-workflow` | Knowledge: AI-ASSET-WORKFLOW.md, including the push rule for the reference-first pipeline |
| `gamedev-kit:nanogpt-api` | Knowledge: NANOGPT-API.md |
| `gamedev-kit:indie-guide` | Knowledge: indie guide |
| `/gamedev-kit:briefing [task]` | Read the docs (all of them for a new game, the relevant parts for an existing one) and give a short brief |
| `/gamedev-kit:new-game [title]` | Scaffold a new game in the current folder |
| `/gamedev-kit:new-asset <group>` | Run the reference-first pipeline for one asset group |
| `/gamedev-kit:game-concept [idea]` | One-page concept in `docs/concept.md` |
| `/gamedev-kit:stack-advisor [question]` | Pick stack options, record them in `000-stack.md` |
| `/gamedev-kit:sync-docs [change]` | Put a lesson or change into this repo (only when you call it) |

## Automatic briefing in every session

When a Claude Code session starts in a game folder where the kit is enabled, the hook `hooks/session-start.js` adds a briefing to Claude's context. You don't need to type anything:

- **New game** (no `docs/specs/000-stack.md` yet): Claude must first read START-HERE, GAME-STACK, AI-ASSET-WORKFLOW and the indie guide in full, give you a short brief, and only then start, even if your first message says "start building".
- **Existing game:** Claude reads START-HERE, the project's `CLAUDE.md` and `docs/specs/`, plus the kit sections that fit the task, and re-reads everything before a new asset group or major system.
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

Git, Node 20+, Python 3.10+, Blender (the version gets pinned per game), and one image API key as a user environment variable: `GEMINI_API_KEY`, `OPENAI_API_KEY` or `NANOGPT_API_KEY`. On Windows:

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
