---
name: game-concept
description: Turn a rough game idea into a one-page concept (hook, genre, comps, pillars, core / secondary / meta loops, minimum-target-dream scope, risks) using the indie development guide, written to docs/concept.md.
when_to_use: The human has a game idea to sharpen, wants a pitch or concept document, or runs /gamedev-kit:game-concept.
argument-hint: "[idea in a sentence]"
---

# Game concept

Idea: $ARGUMENTS

Recommended model: Opus. Tell the human.

1. Read sections 4, 5, 6 and 11 of `${CLAUDE_PLUGIN_ROOT}/docs/indie-game-development-guide.md`.
2. Ask at most three short questions about what is unclear (player fantasy, platform, intended length). Do not ask about art style; that is decided later in the art exploration round.
3. Look up 5–10 comparable titles from the last 3–5 years with web search (price, review count, rough sales via the 30–60× review rule, what reviews praise and complain about). Cite sources.
4. Write `docs/concept.md` (create the folder if needed) with: one-sentence hook; genre and platform; comps table; 3–5 design pillars; core, secondary and meta loop; minimum shippable / target / dream scope with concrete content counts; the riskiest assumptions and the prototype that would test each; a first milestone plan up to the vertical slice.
5. Give your honest assessment of the hook's marketability and the scope for a solo developer with Claude Code, including the main reasons it could fail.
