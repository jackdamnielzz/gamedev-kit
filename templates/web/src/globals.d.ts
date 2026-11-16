// Build-time constants from vite.config.ts.
declare const __APP_VERSION__: string;
declare const __APP_COMMIT__: string;

// Test hooks read by Playwright (tests/e2e). Keep them in every build; they cost nothing.
interface Window {
  __game?: { ready: boolean; version: string; commit: string; serialize: () => string };
  __perf?: { frameMs: number[]; drawCalls?: number };
}
