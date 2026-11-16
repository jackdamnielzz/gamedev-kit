// Seeded PRNG (mulberry32). The state is a plain number stored in the world, so it is
// serialised with saves and replays. Never use Math.random() in src/sim.

export type RngState = number;

export function seedRng(seed: number): RngState {
  return seed | 0;
}

/** Returns a float in [0, 1) and the next state. */
export function nextFloat(state: RngState): { value: number; state: RngState } {
  const next = (state + 0x6d2b79f5) | 0;
  let t = next;
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return { value: ((t ^ (t >>> 14)) >>> 0) / 4294967296, state: next };
}

/** Returns an integer in [min, max] and the next state. */
export function nextInt(state: RngState, min: number, max: number): { value: number; state: RngState } {
  const r = nextFloat(state);
  return { value: min + Math.floor(r.value * (max - min + 1)), state: r.state };
}
