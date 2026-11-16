// Lint rules, including the kit's guard rails for the simulation (GAME-STACK.md, "Known pitfalls"):
// src/sim may not import presentation code or engines, and may not use hidden randomness or time.

import js from "@eslint/js";
import tseslint from "typescript-eslint";

const SIM_ONLY = "src/sim must stay pure and deterministic (GAME-STACK.md, 'Simulation rules').";

export default [
  { ignores: ["dist/", "build/", "public/", "node_modules/", ".venv/", "playwright-report/", "test-results/"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    // Node scripts (tools, hooks, configs).
    files: ["**/*.{js,mjs,cjs}"],
    languageOptions: { globals: { process: "readonly", console: "readonly", URL: "readonly" } },
  },
  {
    files: ["src/sim/**/*.ts"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            { group: ["**/render", "**/render/**", "**/ui", "**/ui/**", "**/audio", "**/audio/**", "**/game", "**/game/**"], message: SIM_ONLY },
            { group: ["phaser", "phaser/**", "pixi.js", "pixi.js/**", "three", "three/**", "@babylonjs/**", "howler"], message: SIM_ONLY },
          ],
        },
      ],
      "no-restricted-properties": [
        "error",
        { object: "Math", property: "random", message: `Use the seeded RNG in the world state. ${SIM_ONLY}` },
        { object: "Date", property: "now", message: `Time is world.tick. ${SIM_ONLY}` },
        { object: "performance", property: "now", message: `Time is world.tick. ${SIM_ONLY}` },
      ],
      "no-restricted-globals": [
        "error",
        ...["window", "document", "localStorage", "sessionStorage", "navigator", "setTimeout", "setInterval", "requestAnimationFrame", "fetch"].map(
          (name) => ({ name, message: SIM_ONLY }),
        ),
      ],
      "no-restricted-syntax": ["error", { selector: "NewExpression[callee.name='Date']", message: `Time is world.tick. ${SIM_ONLY}` }],
    },
  },
];
