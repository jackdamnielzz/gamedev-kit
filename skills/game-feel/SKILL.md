---
name: game-feel
description: Game feel for Niels's games - response, feedback and forgiveness with concrete starting values (input buffer, coyote time, jump arcs, hit-stop, trauma-based screen shake, squash and stretch, camera, UI easing, sound variation) per genre, where each value lives (sim in ticks vs render), data/feel.json, and how an agent verifies feel it cannot feel (tick tests, filmstrips, latency check, the human's tuning panel, the feel gate).
when_to_use: Building or tuning controls, movement, combat, camera, hit feedback, juice, menus or UI motion; a playtester says something feels slow, floaty, stiff or unresponsive; preparing the feel gate before the vertical slice.
---

# Game feel

The guide lives in `${CLAUDE_PLUGIN_ROOT}/docs/GAME-FEEL.md`. Read it before building or changing controls, combat, camera or UI motion; do not rely on memory of it.

Section map: Summary · 1 Where feel lives in the architecture · 2 Starting values (response and control, impact feedback, camera, UI, per genre) · 3 How the agent verifies feel · 4 Accessibility · 5 Pitfalls · Sources.

Rules when using it:

- Response first, juice second: fix latency and control curves before adding effects.
- Every feel value lives in `data/feel.json` with a range in the schema; no magic numbers in code.
- Timing that changes outcomes (buffer, coyote, hit-stop that delays gameplay, cancel windows) lives in the sim, in ticks; shake, flashes, particles and tweens live in the render layer.
- Prove the rules with tick tests and check the look with a filmstrip you read yourself; report the measured input latency.
- The human tunes in the dev tuning panel; you commit the tuned values with a dated decision. Do not tune by your own taste.
- Shake, flash and motion always get accessibility settings.
- The project's own specs win over the starting values in the guide.
- Recommended model: Opus for the feel spec and reviewing filmstrips; Sonnet for implementing the controls, panel and tests.
