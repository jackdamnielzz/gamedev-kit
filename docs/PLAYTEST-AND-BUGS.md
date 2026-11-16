# Playtests and bugs — from a play session to a regression test

> **Master copy:** the GitHub repo `jackdamnielzz/gamedev-kit`, folder `docs/`. Copies elsewhere follow the repo; change the repo first.

16 November 2026 · Niels. In the kit the human designs and playtests and the agents build. This page is the loop between the two: how a playtest is prepared and run, how notes become decisions, and how a bug a player saw becomes a replay file and a regression test, so it can never come back unnoticed. It builds on the deterministic sim from `GAME-STACK.md` (same seed and same commands give the same result), which makes most bugs reproducible for almost nothing.

## Summary

```
build → playtest → session notes → triage → spec change (human) or bug
                                                     ↓
               in-game bug report (seed + command log + version)
                                                     ↓
          tests/fixtures/replays/<id>.json → failing test → fix → passing test
```

- One question per playtest, written down before it starts.
- Notes are observations ("3 of 5 testers never found the shop"), not opinions ("players want a bigger shop").
- The agent triages; the human decides anything that changes rules, economy, scope or story.
- Every bug in the sim gets a replay file and a test that fails before the fix and passes after it.
- `docs/STATUS.md` lists the known issues; the bug list itself lives in GitHub Issues or `docs/BUGS.md`.

## 1. Kinds of playtest

| Kind | Who | When | Main question |
| --- | --- | --- | --- |
| Bot run | The agent (`npm run bots`) | Every gameplay change | Balance, softlocks, exploits (`GAME-STACK.md`, "Bots that play the game") |
| Self-test | The human | After every milestone build, at least weekly | Does it do what the spec says? Is it fun yet? |
| Feel gate | The human | Before the vertical slice | Does the core verb feel good with greybox art? (`GAME-FEEL.md`, section 3) |
| Friends | 2–5 people | Prototype and vertical slice | Do they understand the goal without help? |
| Strangers | Discord, itch.io, Steam Playtest | Vertical slice onwards | Would they keep playing? Where do they quit? |

The indie guide (sections 6.2 and 13.3) covers why and when; this page covers how.

## 2. Preparing a playtest build (the agent)

- The version and short commit hash are visible in the main menu and in every bug report.
- Dev tools are off (tuning panel, cheats, debug overlay), except the **bug report key**.
- Telemetry, if any, asks for consent first and stores no personal data (AVG/GDPR).
- A known-issues list (from `docs/STATUS.md`) goes with the build, so testers do not report them again.
- The session plan in `docs/playtests/<YYYY-MM-DD>-plan.md`: the one question, what the tester is asked to do, and at most five questions for afterwards. Use `docs/playtests/TEMPLATE-session.md`.
- Web: a separate URL or itch.io page per build; Steam: a playtest branch.

## 3. Running a session (the human)

- Watch without explaining. If you must help, write down when and why: every hint is a finding.
- Note the time of every moment of confusion, boredom, surprise or delight, and where the tester stopped.
- Afterwards ask open questions: "What were you trying to do?", "When did you want to stop?", "What would you tell a friend about it?" Not "Did you like it?"
- The strongest signal: does the tester ask to play again?
- Rough notes, voice memos or a screen recording are fine; the agent writes them up.

## 4. Writing up and triage (the agent)

1. Turn the raw notes into `docs/playtests/<YYYY-MM-DD>-<tester>.md` with the session template: build, tester profile, what happened in order, quotes, confusion points, where they quit, answers.
2. After a round of sessions, write `docs/playtests/<YYYY-MM-DD>-triage.md`. Group findings by kind and count how many testers hit each one:

| Kind | Goes to |
| --- | --- |
| Bug (something breaks or is wrong by the spec) | A bug entry (section 7), with a replay if the report has one |
| UX (unclear, hard to find, misread) | A task against the existing spec; a spec change if the fix changes rules |
| Feel (slow, floaty, stiff) | A feel task: values in `data/feel.json` for the human to tune (`GAME-FEEL.md`) |
| Balance (too easy, too hard, dominant strategy) | A data change, checked with a bot run; economy changes need a spec decision |
| Content (too little, repetitive) | The scope list; story issues against `STORY-AND-NARRATIVE.md` |
| Idea (a tester's suggestion) | The "later" list, never the current sprint |

3. Order by severity × how many testers hit it. Present the top five to the human with a proposed action each. The human decides; decisions go into the matching spec with a date.

## 5. Bug reports from inside the game

Every game gets a bug report action from the first playable build: a key (F8) and a menu button. It writes one JSON file:

| Field | What |
| --- | --- |
| `format` | Replay format version (currently 1) |
| `id` | `bug-<YYYYMMDD>-<HHMMSS>` |
| `game_version`, `commit` | From the build |
| `seed`, `config` | The values the run was created with |
| `start_save` | `null` when the run started from `seed`; otherwise the serialised world it started from (after loading a save) |
| `ticks` | The tick at the moment of the report |
| `commands` | Every command the sim received since the start (or since `start_save`), each with its `tick` |
| `report` | `created_at`, `platform` (browser or OS, screen size), `user_note`, the last 200 log lines, and an optional `screenshot_png_base64` |

- The game layer keeps the command log: every command it passes to the sim is appended with its tick. Loading a save starts a new log with `start_save` set to that save. If the log grows very large, rebase it: `start_save` = the current serialised world, empty `commands`.
- Web: offer the file as a download and copy a short summary to the clipboard. Godot: write to `user://bugreports/` and show the folder.
- Release builds also catch crashes: `window.onerror` and `unhandledrejection` on the web, error logging in Godot, and offer the same report. Sending reports anywhere (a form, Sentry) only with the player's consent and without personal data.
- The report never contains API keys, account names or file paths outside the game.

## 6. From report to regression test

A replay file is a bug report without the `report` block, plus an `expect` block:

```json
{
  "format": 1,
  "id": "bug-20261116-201502",
  "game_version": "0.3.1",
  "commit": "abc1234",
  "seed": 1234,
  "config": {},
  "start_save": null,
  "ticks": 1800,
  "commands": [{ "tick": 12, "type": "sell", "item": "ore", "count": 2 }],
  "expect": { "invariants": ["moneyNeverNegative"], "state_hash": null },
  "note": "Gold went negative after selling twice in one tick"
}
```

1. Copy the report to `tests/fixtures/replays/<id>.json`, drop `report` (screenshots are large) and add `expect` and `note`.
2. **Make it fail first.** Name an invariant that describes the bug (registered in `tests/helpers/invariants.ts`, Godot: `tests/invariants.gd`) and run the replay test: it must fail. If it passes, the replay does not reproduce the bug: find out why before fixing anything.
3. Fix the sim. The replay test now passes. Run `npm run check` and the bots.
4. Optionally pin `state_hash` (the test prints it) so any later change to that run's outcome is noticed. When a rule changes on purpose, update the hash with a dated note in the replay's `note`.
5. A replay that no longer applies (the mechanic was removed) moves to `tests/fixtures/replays/archive/` with a note; it is never silently deleted.

The replay and determinism tests in the templates do this out of the box: every replay runs twice and must give the same hash, survives a save-and-load in the middle, and checks its invariants on every tick.

**Bugs a replay cannot catch** (rendering, UI, audio, input handling): reproduce with a Playwright test (web) or a scripted Godot run with a screenshot, and keep that test.

## 7. Tracking bugs

- Small projects: `docs/BUGS.md`, one line per bug. Larger ones: GitHub Issues with labels `bug`, `severity:crash|blocker|major|minor|cosmetic`, `area:<system>`.
- Each bug has: steps or a replay file, expected and actual result, build version, platform, severity (indie guide section 13.2).
- Open bugs above `minor` are listed under "Known issues" in `docs/STATUS.md`.
- Every fixed bug has a test (a replay, a unit test or an end-to-end test). No test, not fixed.

## 8. Checklist

| # | Do this |
| --- | --- |
| 1 | Version and commit visible in the menu and in every report |
| 2 | Bug report key from the first playable build, writing the replay format |
| 3 | The game layer keeps a command log; saves restart it with `start_save` |
| 4 | One question per playtest, written in the session plan |
| 5 | Observations, not opinions, with a count of testers |
| 6 | Triage by kind; the human decides spec, economy, scope and story changes |
| 7 | Every sim bug: replay file → failing test → fix → passing test |
| 8 | Non-sim bugs: a Playwright or scripted Godot test |
| 9 | Known issues in `docs/STATUS.md`; the list ships with every playtest build |
| 10 | Crash reports and telemetry only with consent and without personal data |
