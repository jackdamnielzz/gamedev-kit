// The simulation: pure, deterministic game rules. This file is a placeholder that shows the
// contract every game keeps (GAME-STACK.md, "Game runtime"); replace the world and commands
// with the real game, keep the four exported functions and their meaning.
//
//   createWorld(seed, config) -> World     a new run
//   step(world, commands)     -> World     one tick; returns the next world
//   serialize(world)          -> string    stable JSON (same world, same string)
//   deserialize(text)         -> World
//
// No imports from render/, ui/, audio/, game/; no DOM, no Math.random, no Date.now
// (enforced by eslint.config.js). Time is world.tick.

import { nextInt, seedRng, type RngState } from "./rng";

export const SAVE_VERSION = 1;

export interface Config {
  startValue?: number;
}

export type Command = { type: "noop" } | { type: "add"; amount: number };

export interface World {
  version: number;
  tick: number;
  rng: RngState;
  value: number;
  sparks: number;
}

export function createWorld(seed: number, config: Config = {}): World {
  return { version: SAVE_VERSION, tick: 0, rng: seedRng(seed), value: config.startValue ?? 0, sparks: 0 };
}

export function step(world: World, commands: readonly Command[]): World {
  let { value, rng, sparks } = world;
  for (const c of commands) {
    if (c.type === "add") value += c.amount;
  }
  // Example of seeded randomness: an occasional spark.
  const roll = nextInt(rng, 1, 100);
  rng = roll.state;
  if (roll.value === 1) sparks += 1;
  return { ...world, tick: world.tick + 1, rng, value, sparks };
}

export function serialize(world: World): string {
  // Fixed key order keeps the string (and its hash) stable.
  const { version, tick, rng, value, sparks } = world;
  return JSON.stringify({ version, tick, rng, value, sparks });
}

export function deserialize(text: string): World {
  const data = JSON.parse(text) as World;
  if (data.version !== SAVE_VERSION) {
    throw new Error(`save version ${data.version} needs a migration to ${SAVE_VERSION}`);
  }
  return data;
}
