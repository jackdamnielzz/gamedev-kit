---
name: game-stack
description: Niels's Claude-driven game dev stack (TypeScript + Vite browser games, Phaser / PixiJS / Three.js, pure deterministic sim, zod data, Vitest / Playwright / bots, Electron for Steam) with repo layout, npm scripts, agent workflow, CI, stack recipes per game type and templates. Use when planning, scaffolding, structuring or reviewing any game project, choosing a layer of the stack, writing CLAUDE.md or specs, or setting up tests, CI or packaging.
when_to_use: Any game-dev architecture, tooling, repo-structure, testing, CI/CD, packaging or agent-workflow question in one of Niels's games.
---

# Game stack

The full catalogue lives in `${CLAUDE_PLUGIN_ROOT}/docs/GAME-STACK.md`. Read the sections you need with the Read tool before answering or building; do not rely on memory of it.

Section map (use Grep on the headings to jump):

- Purpose and how to use this document
- Core principles (nine rules, including "Reference first")
- Stack overview (one default per layer, with alternatives)
- Game runtime (sim / game / render / ui / audio / data layers, determinism, saves)
- Art pipeline (reference-first summary, headless Blender, sprites from 3D, pixel-art look, UI, AI images, manifest, visual review)
- Audio pipeline
- Levels and content data
- Testing, bots and performance guards
- Repository layout and scripts
- Claude Code workflow (roles, model choice, task briefs, specs, git rules)
- CI/CD, deployment and packaging
- Stack recipes by game type
- Known pitfalls
- Templates (CLAUDE.md, feature spec, Blender reference-plane helper, comparison script, sprite recipe skeleton)

Rules when using it:

- If the current project has `docs/specs/000-stack.md`, the choices recorded there win over the catalogue's defaults. Do not reopen recorded decisions unless the human asks.
- The stack recipes are technical starting points, not a visual style. The look of every game is chosen per game in the art exploration step.
- For anything about art or audio assets, also load the `asset-workflow` skill: the reference-first pipeline is the default and must be proposed proactively.
- Tell the human which Claude model you recommend for the work at hand (Opus for coordination, specs and art direction; Sonnet for most building; Haiku for mechanical edits).
