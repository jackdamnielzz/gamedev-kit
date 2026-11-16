// Runs replay files (tests/fixtures/replays/*.json, format in PLAYTEST-AND-BUGS.md) against the
// sim. Used by the determinism and replay tests, and by bug fixing.

import { createHash } from "node:crypto";
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { createWorld, deserialize, serialize, step, type Command, type Config, type World } from "../../src/sim";
import { invariants } from "./invariants";

export const REPLAY_DIR = join(process.cwd(), "tests", "fixtures", "replays");

export interface Replay {
  format: number;
  id: string;
  seed: number;
  config?: Config;
  start_save?: string | Record<string, unknown> | null;
  ticks: number;
  commands: Array<{ tick: number; type: string; [key: string]: unknown }>;
  expect?: { invariants?: string[]; state_hash?: string | null };
  note?: string;
  report?: { state_hash?: string };
}

/** Same hash as the in-game bug report: sha256 of serialize(world), first 16 hex characters. */
export function hashWorld(world: World): string {
  return createHash("sha256").update(serialize(world), "utf8").digest("hex").slice(0, 16);
}

/** Every replay in the folder (not in archive/), sorted by file name. */
export function loadReplays(dir = REPLAY_DIR): Replay[] {
  return readdirSync(dir)
    .filter((f) => f.endsWith(".json"))
    .sort()
    .map((f) => JSON.parse(readFileSync(join(dir, f), "utf8")) as Replay);
}

export interface RunOptions {
  /** Check expect.invariants after every tick. */
  checkInvariants?: boolean;
  /** Serialise and deserialise the world at this tick (save/load in the middle of a run). */
  saveLoadAt?: number;
}

export interface RunResult {
  world: World;
  hash: string;
  violations: string[];
}

export function runReplay(replay: Replay, options: RunOptions = {}): RunResult {
  if (replay.format !== 1) throw new Error(`${replay.id}: unknown replay format ${replay.format}`);
  const names = options.checkInvariants ? (replay.expect?.invariants ?? []) : [];
  for (const name of names) {
    if (!invariants[name]) throw new Error(`${replay.id}: unknown invariant "${name}" (add it to tests/helpers/invariants.ts)`);
  }

  const byTick = new Map<number, Command[]>();
  for (const { tick, ...command } of replay.commands) {
    if (tick < 0 || tick >= replay.ticks) throw new Error(`${replay.id}: command at tick ${tick} is outside 0..${replay.ticks - 1}`);
    const list = byTick.get(tick) ?? [];
    list.push(command as unknown as Command);
    byTick.set(tick, list);
  }

  const save = replay.start_save;
  let world = save
    ? deserialize(typeof save === "string" ? save : JSON.stringify(save))
    : createWorld(replay.seed, replay.config ?? {});

  const violations: string[] = [];
  const seen = new Set<string>();
  for (let t = 0; t < replay.ticks; t++) {
    if (options.saveLoadAt === t) world = deserialize(serialize(world));
    world = step(world, byTick.get(t) ?? []);
    for (const name of names) {
      if (seen.has(name)) continue;
      const problem = invariants[name]!(world);
      if (problem) {
        seen.add(name);
        violations.push(`${name} broken after relative tick ${t}: ${problem}`);
      }
    }
  }
  return { world, hash: hashWorld(world), violations };
}
