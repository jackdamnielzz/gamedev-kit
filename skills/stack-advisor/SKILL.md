---
name: stack-advisor
description: Recommend one option per stack layer (renderer, physics, UI, levels, art build routes, reference route, audio, packaging) for a specific game, based on GAME-STACK.md and AI-ASSET-WORKFLOW.md, and record the choices in docs/specs/000-stack.md.
when_to_use: Choosing or revisiting the tech stack for a game, comparing renderer or tool options, or running /gamedev-kit:stack-advisor.
argument-hint: "[what to decide, e.g. 'renderer for an isometric RTS']"
---

# Stack advisor

Question: $ARGUMENTS

Recommended model: Opus. Tell the human.

1. Read `docs/concept.md` and `docs/specs/000-stack.md` if they exist. Decisions already recorded there are final unless the human explicitly reopens them.
2. Read "Stack overview", "Stack recipes by game type" and "Known pitfalls" in `${CLAUDE_PLUGIN_ROOT}/docs/GAME-STACK.md`, and the "Decision checklist for a new game" in `${CLAUDE_PLUGIN_ROOT}/docs/AI-ASSET-WORKFLOW.md`.
3. For each open layer, recommend the default unless the game clearly needs an alternative; give the reason in one line and the main trade-off. Check versions or prices that may have changed with a web search before stating them.
4. The art build route (A Blender from primitives, B image-to-3D + Blender, C code-built UI, or shipping images directly) depends on asset type; the visual style itself is not decided here.
5. After the human agrees, write the choices into `docs/specs/000-stack.md` with dated Decisions entries.
