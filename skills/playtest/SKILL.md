---
name: playtest
description: Run the playtest and bug loop in one of Niels's games - prepare a playtest build and session plan, write raw notes up as session reports, triage findings (bug, UX, feel, balance, content, idea) for the human to decide, and turn bug reports (seed + command log) into replay files and failing-then-passing regression tests.
when_to_use: The human is about to playtest or hand a build to testers, shares playtest notes or a bug report file, reports a bug, or runs /gamedev-kit:playtest.
argument-hint: "[plan | notes | triage | bug <report file or description>]"
---

# Playtest

Mode: $ARGUMENTS (ask if empty: plan a round, write up notes, triage a round, or fix a bug).

Read `${CLAUDE_PLUGIN_ROOT}/docs/PLAYTEST-AND-BUGS.md` first, and the project's `docs/STATUS.md`. Recommended model: Opus for triage and planning; Sonnet for writing a replay test and a fix against a clear report. Tell the human.

## plan

1. Ask the human for the one question this round must answer, if it is not clear.
2. Check the build: version and commit in the menu, dev tools off, bug report key on, known issues from `docs/STATUS.md`.
3. Write `docs/playtests/<YYYY-MM-DD>-plan.md` from `docs/playtests/TEMPLATE-session.md`.

## notes

Turn the human's raw notes, memo transcript or recording summary into one `docs/playtests/<YYYY-MM-DD>-<tester>.md` per session. Keep observations and quotes; do not add interpretations the notes do not support. Ask about gaps instead of guessing.

## triage

Read every session file of the round and write `docs/playtests/<YYYY-MM-DD>-triage.md`: findings grouped by kind with the number of testers who hit each, ordered by severity × count, and a proposed action per finding. Present the top five to the human and wait. Anything that changes rules, economy, scope or story is the human's decision; record it with a date in the matching spec. Ideas go to the later list.

## bug

1. With a bug report file: copy it to `tests/fixtures/replays/<id>.json`, remove the `report` block, add `expect` and `note`. Without one: ask for steps, or write the shortest command list that reproduces it.
2. Add or reuse an invariant that describes the bug and run the replay test. It must fail. If it passes, the replay does not reproduce the bug: say so and investigate before changing code.
3. Fix it, run the replay test, the project's check command and the bots, and paste the results.
4. Bugs outside the sim (rendering, UI, input, audio): a Playwright or scripted Godot test instead of a replay.
5. Update the bug list (GitHub Issues or `docs/BUGS.md`) and "Known issues" in `docs/STATUS.md`.
