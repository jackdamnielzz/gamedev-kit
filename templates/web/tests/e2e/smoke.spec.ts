// The game boots without errors, and an in-game bug report replays to the exact same state
// (PLAYTEST-AND-BUGS.md, sections 5 and 6).

import { readFileSync } from "node:fs";
import { expect, test } from "@playwright/test";
import { runReplay, type Replay } from "../helpers/sim-harness";

test("boots without console errors and shows the game", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(m.text());
  });
  await page.goto("/?seed=7");
  await page.waitForFunction(() => window.__game?.ready === true);
  await page.waitForTimeout(500);
  await page.screenshot({ path: "build/previews/e2e-smoke.png" });
  expect(errors).toEqual([]);
});

test("a bug report replays to the reported state", async ({ page }) => {
  page.on("dialog", (d) => void d.accept("e2e test report"));
  await page.goto("/?seed=7");
  await page.waitForFunction(() => window.__game?.ready === true);
  for (let i = 0; i < 5; i++) {
    await page.keyboard.press("Space");
    await page.waitForTimeout(50);
  }
  const download = page.waitForEvent("download");
  await page.keyboard.press("F8");
  const report = JSON.parse(readFileSync(await (await download).path(), "utf8")) as Replay & { report: { state_hash: string } };
  expect(report.commands.length).toBe(5);
  expect(runReplay(report).hash).toBe(report.report.state_hash);
});
