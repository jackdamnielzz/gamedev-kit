---
name: briefing
description: Read the gamedev-kit documentation before working on a game - START-HERE.md first, then the stack, asset workflow and indie guide (in full for a new game, the relevant sections for an existing one) - and give the human a short brief of the rules, open questions and recommended model.
when_to_use: At the start of a session in a game project, before starting a new game or a new major system or asset group, when the human says "read the docs", "brief yourself" or runs /gamedev-kit:briefing. The kit's SessionStart hook also points here.
argument-hint: "[task you are about to start]"
---

# Briefing

Task about to start: $ARGUMENTS

1. Read `${CLAUDE_PLUGIN_ROOT}/docs/START-HERE.md` in full with the Read tool.
2. Work out which case applies:
   - **New game**: the folder has no `docs/specs/000-stack.md`. Read all of these in full, in order: `GAME-STACK.md`, `AI-ASSET-WORKFLOW.md`, `indie-game-development-guide.md` (all in `${CLAUDE_PLUGIN_ROOT}/docs/`), plus the overview of `NANOGPT-API.md`.
   - **Existing game**: read the project's `CLAUDE.md`, `docs/concept.md` and every file in `docs/specs/`. Then read the kit sections that match the task (art and animation: `AI-ASSET-WORKFLOW.md`; architecture, testing and tooling: `GAME-STACK.md`; scope, release and marketing: the indie guide). If the task is a new asset group, a new major system or a stack change, read those documents in full.
3. Reply to the human with a brief of at most 10 lines:
   - the rules from START-HERE that matter for this task;
   - the animation route you would use, if art is involved;
   - the questions you still need answered;
   - the Claude model you recommend for the next step.
4. Only then start the task. Everything in English.
