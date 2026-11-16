// Performance guard (`npm run perf`) against perf/budgets.json. The game measures its own work per
// frame in window.__perf.frameMs (update + render, not the vsync wait) and may report draw calls in
// window.__perf.drawCalls. Load a heavy scene with ?perf=1 once the game has one.

import { appendFileSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { expect, test } from "@playwright/test";

const budgets = JSON.parse(readFileSync("perf/budgets.json", "utf8")) as {
  frame_time_p95_ms: number;
  draw_calls_max: number;
  js_heap_mb_max: number;
  initial_download_mb_max: number;
};

function p95(values: number[]): number {
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.min(sorted.length - 1, Math.floor(sorted.length * 0.95))] ?? 0;
}

test("stays within perf/budgets.json @perf", async ({ page }) => {
  await page.goto("/?perf=1&seed=1");
  await page.waitForFunction(() => window.__game?.ready === true);
  await page.waitForTimeout(5000);

  const m = await page.evaluate(() => {
    const resources = performance.getEntriesByType("resource") as PerformanceResourceTiming[];
    const nav = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming | undefined;
    const bytes = resources.reduce((sum, r) => sum + r.transferSize, nav?.transferSize ?? 0);
    const memory = (performance as unknown as { memory?: { usedJSHeapSize: number } }).memory;
    return {
      frameMs: window.__perf?.frameMs ?? [],
      drawCalls: window.__perf?.drawCalls ?? null,
      heapMb: memory ? memory.usedJSHeapSize / 2 ** 20 : null,
      downloadMb: bytes / 2 ** 20,
    };
  });

  const result = {
    date: new Date().toISOString(),
    frame_time_p95_ms: Number(p95(m.frameMs).toFixed(2)),
    frames: m.frameMs.length,
    draw_calls: m.drawCalls,
    js_heap_mb: m.heapMb === null ? null : Number(m.heapMb.toFixed(1)),
    initial_download_mb: Number(m.downloadMb.toFixed(2)),
  };
  mkdirSync("build/reports", { recursive: true });
  writeFileSync("build/reports/perf.json", JSON.stringify(result, null, 2));
  if (!process.env.CI) appendFileSync("perf/history.jsonl", JSON.stringify(result) + "\n");

  expect(m.frameMs.length, "window.__perf.frameMs is empty: the game loop does not report frame times").toBeGreaterThan(30);
  expect(result.frame_time_p95_ms).toBeLessThanOrEqual(budgets.frame_time_p95_ms);
  if (result.draw_calls !== null) expect(result.draw_calls).toBeLessThanOrEqual(budgets.draw_calls_max);
  if (result.js_heap_mb !== null) expect(result.js_heap_mb).toBeLessThanOrEqual(budgets.js_heap_mb_max);
  expect(result.initial_download_mb).toBeLessThanOrEqual(budgets.initial_download_mb_max);
});
