// Property tests (fast-check): random command sequences must keep the sim's invariants and
// stay deterministic. Example for the placeholder sim: replace the command generator and the
// properties with the real game's commands and rules (money never negative, no unit outside the
// map, save -> load -> save identical).

import fc from "fast-check";
import { describe, expect, it } from "vitest";
import { createWorld, deserialize, serialize, step, type Command } from "../../src/sim";

const command: fc.Arbitrary<Command> = fc.oneof(
  fc.constant<Command>({ type: "noop" }),
  fc.integer({ min: -5, max: 5 }).map<Command>((amount) => ({ type: "add", amount })),
);
const run = fc.array(fc.array(command, { maxLength: 3 }), { maxLength: 200 });

function play(seed: number, ticks: Command[][]) {
  let world = createWorld(seed);
  for (const commands of ticks) world = step(world, commands);
  return world;
}

describe("sim properties", () => {
  it("same seed and commands give the same serialised state", () => {
    fc.assert(fc.property(fc.integer(), run, (seed, ticks) => serialize(play(seed, ticks)) === serialize(play(seed, ticks))));
  });

  it("save -> load -> save is identical at any point", () => {
    fc.assert(
      fc.property(fc.integer(), run, (seed, ticks) => {
        const text = serialize(play(seed, ticks));
        expect(serialize(deserialize(text))).toBe(text);
      }),
    );
  });

  it("the tick counter advances by exactly one per step", () => {
    fc.assert(fc.property(fc.integer(), run, (seed, ticks) => play(seed, ticks).tick === ticks.length));
  });
});
