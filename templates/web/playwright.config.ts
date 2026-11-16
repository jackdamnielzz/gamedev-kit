import { defineConfig, devices } from "@playwright/test";

// End-to-end tests run against the production build (`vite preview`).
// CHROME_PATH lets a machine use an installed Chrome instead of `npx playwright install chromium`.
export default defineConfig({
  testDir: "tests/e2e",
  outputDir: "build/test-results",
  reporter: process.env.CI ? [["list"], ["html", { outputFolder: "build/reports/playwright", open: "never" }]] : "list",
  use: {
    baseURL: "http://127.0.0.1:4173",
    launchOptions: process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {},
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: "npm run build && npm run preview -- --port 4173 --strictPort --host 127.0.0.1",
    url: "http://127.0.0.1:4173",
    reuseExistingServer: !process.env.CI,
    timeout: 180_000,
  },
});
