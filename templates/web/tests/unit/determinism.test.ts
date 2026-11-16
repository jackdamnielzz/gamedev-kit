// Same seed + same commands = same state; save/load in the middle changes nothing.
// Runs on every replay in tests/fixtures/replays/ (GAME-STACK.md, "Test layers").

import { describe, expect, it } from "vitest";
import { createWorld, deserialize, serialize } from "../../src/sim";
import { loadReplays, runReplay } from "../helpers/sim-harness";

const replays = loadReplays();

describe("determinism", () => {
  it("has at least one replay fixture", () => {
    expect(replays.length).toBeGreaterThan(0);
  });

  it("serialize -> deserialize -> serialize is identical", () => {
    const world = createWorld(42);
    expect(serialize(deserialize(serialize(world)))).toBe(serialize(world));
  });

  for (const replay of replays) {
    it(`${replay.id}: two runs give the same state`, () => {
      expect(runReplay(replay).hash).toBe(runReplay(replay).hash);
    });

    it(`${replay.id}: save and load halfway gives the same state`, () => {
      const straight = runReplay(replay).hash;
      const reloaded = runReplay(replay, { saveLoadAt: Math.floor(replay.ticks / 2) }).hash;
      expect(reloaded).toBe(straight);
    });
  }
});
