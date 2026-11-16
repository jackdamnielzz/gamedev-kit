// In-game bug report (PLAYTEST-AND-BUGS.md, section 5): the replay of the current run plus
// context, downloaded as one JSON file. No personal data, no keys, no paths.

import { serialize, type World } from "../sim";
import type { CommandLog } from "./commandLog";

const logTail: string[] = [];

/** Keep the last 200 log lines for bug reports. */
export function gameLog(line: string): void {
  logTail.push(`${new Date().toISOString()} ${line}`);
  if (logTail.length > 200) logTail.shift();
}

export async function stateHash(world: World): Promise<string> {
  const bytes = new TextEncoder().encode(serialize(world));
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, 16);
}

function stamp(d: Date): string {
  const p = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
}

export async function buildBugReport(log: CommandLog, world: World, canvas: HTMLCanvasElement | null, userNote: string) {
  const now = new Date();
  return {
    id: `bug-${stamp(now)}`,
    game_version: __APP_VERSION__,
    commit: __APP_COMMIT__,
    ...log.toReplay(world),
    report: {
      created_at: now.toISOString(),
      platform: { userAgent: navigator.userAgent, screen: `${screen.width}x${screen.height}` },
      user_note: userNote,
      state_hash: await stateHash(world),
      log_tail: [...logTail],
      screenshot_png_base64: canvas ? canvas.toDataURL("image/png").split(",")[1] : null,
    },
  };
}

export function downloadJson(data: unknown, filename: string): void {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}
