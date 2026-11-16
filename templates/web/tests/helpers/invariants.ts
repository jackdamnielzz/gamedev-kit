// Named invariants that replay files can ask for (`expect.invariants`). Each returns null when
// the world is fine, or a short message when it is not. Add one per bug class
// (PLAYTEST-AND-BUGS.md, section 6), e.g. moneyNeverNegative, noUnitOutsideMap.

import type { World } from "../../src/sim";

export const invariants: Record<string, (world: World) => string | null> = {
  tickNeverNegative: (w) => (w.tick >= 0 ? null : `tick is ${w.tick}`),
};
