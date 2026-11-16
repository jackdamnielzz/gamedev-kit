// Every replay keeps its promises: its invariants hold on every tick, and a pinned state_hash
// still matches. A bug's replay must fail here before the fix (PLAYTEST-AND-BUGS.md, section 6).

import { describe, expect, it } from "vitest";
import { loadReplays, runReplay } from "../helpers/sim-harness";

describe("replays", () => {
  for (const replay of loadReplays()) {
    it(`${replay.id}${replay.note ? ` (${replay.note})` : ""}`, () => {
      const result = runReplay(replay, { checkInvariants: true });
      expect(result.violations).toEqual([]);
      const pinned = replay.expect?.state_hash;
      if (pinned) expect(result.hash, "state_hash changed: a rule changed this run's outcome").toBe(pinned);
      else console.info(`${replay.id} state_hash=${result.hash}`);
    });
  }
});
