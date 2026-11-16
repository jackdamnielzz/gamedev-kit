import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    // Playwright specs (tests/e2e/*.spec.ts) are not Vitest tests.
    include: ["tests/unit/**/*.test.ts", "src/**/*.test.ts"],
  },
});
