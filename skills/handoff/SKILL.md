---
name: handoff
description: End a work session in one of Niels's games cleanly - run the checks, update docs/STATUS.md (where the project stands, what works, what is in progress, next steps, what waits for the human, known issues, last sessions), commit it, and give the human a short summary, so the next session or agent can start without guessing.
when_to_use: The human says to stop, wrap up, pause or hand over; before a long break or a context compaction; after a milestone; or when the human runs /gamedev-kit:handoff.
argument-hint: "[anything the human wants recorded]"
---

# Handoff

Extra notes from the human: $ARGUMENTS

Recommended model: Sonnet (Haiku is enough when little changed). Tell the human.

1. Run the project's check command (web: `npm run check`; Godot: the headless test run from `CLAUDE.md`) and, if gameplay changed this session, the bots. Keep the results.
2. List uncommitted changes and open branches (`git status`, `git branch`). Commit finished work on its branch; do not commit half-done work to `main`. Mention anything left uncommitted.
3. Update `docs/STATUS.md` (create it from `${CLAUDE_PLUGIN_ROOT}/templates/project/docs/STATUS.md` if it is missing):
   - "Where we are": phase, milestone, build, the check results from step 1;
   - "Works now", "In progress" (with branches), "Next steps" in order;
   - "Waiting for the human": every pick, decision or playtest you need, with the path to the material;
   - "Known issues": open bugs above minor;
   - "Last sessions": add today at the top in one or two lines, keep three.
   Write facts only; no plans the human did not agree to are listed as decisions.
4. Add a line to `docs/MADE-WITH-AI.md` if a workflow problem was solved this session.
5. Commit `docs/STATUS.md` (and the log) with the message "Update status".
6. Reply to the human in at most eight lines: what changed, what is next, what waits for them.
