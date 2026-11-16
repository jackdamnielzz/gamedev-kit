// Glue (src/game in GAME-STACK.md terms): fixed-timestep loop, input -> commands -> sim,
// sim state -> drawing. A placeholder: replace the canvas drawing with the chosen renderer
// (Phaser, PixiJS, Three.js) in src/render and the HUD in src/ui; keep the loop, the command
// log, the bug report key and the window.__game / window.__perf test hooks.

import { createWorld, serialize, step, type Command, type Config } from "./sim";
import { CommandLog } from "./game/commandLog";
import { buildBugReport, downloadJson, gameLog } from "./game/bugReport";

const TICK_RATE = 30; // 60 for precise action games (GAME-FEEL.md, section 1)
const TICK_MS = 1000 / TICK_RATE;
const MAX_TICKS_PER_FRAME = 5;

const params = new URLSearchParams(location.search);
const seed = Number(params.get("seed") ?? Math.floor(Math.random() * 2 ** 31));
const config: Config = {};
let world = createWorld(seed, config);
const log = new CommandLog(seed, config);
const pending: Command[] = [];

const canvas = document.querySelector<HTMLCanvasElement>("#game");
const ctx = canvas?.getContext("2d") ?? null;

window.__perf = { frameMs: [] };
window.__game = { ready: false, version: __APP_VERSION__, commit: __APP_COMMIT__, serialize: () => serialize(world) };

addEventListener("keydown", (e) => {
  if (e.code === "Space") pending.push({ type: "add", amount: 1 });
  if (e.code === "F8") {
    e.preventDefault();
    void reportBug();
  }
});
addEventListener("error", (e) => gameLog(`error: ${e.message}`));
addEventListener("unhandledrejection", (e) => gameLog(`unhandled rejection: ${String(e.reason)}`));

async function reportBug(): Promise<void> {
  const note = window.prompt("What went wrong? (optional)") ?? "";
  const report = await buildBugReport(log, world, canvas, note);
  downloadJson(report, `${report.id}.json`);
  gameLog(`bug report ${report.id} saved`);
}

function draw(): void {
  if (!ctx || !canvas) return;
  ctx.fillStyle = "#1b1b24";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#e8e8e8";
  ctx.font = "16px monospace";
  ctx.fillText(`tick ${world.tick}   value ${world.value}   sparks ${world.sparks}`, 16, 32);
  ctx.fillText(`Space: add   F8: bug report   v${__APP_VERSION__} (${__APP_COMMIT__})`, 16, canvas.height - 16);
}

let last = performance.now();
let acc = 0;
function frame(now: number): void {
  const t0 = performance.now();
  acc += now - last;
  last = now;
  let ticks = 0;
  while (acc >= TICK_MS && ticks < MAX_TICKS_PER_FRAME) {
    const commands = pending.splice(0);
    log.record(world, commands);
    world = step(world, commands);
    acc -= TICK_MS;
    ticks += 1;
  }
  if (ticks === MAX_TICKS_PER_FRAME) acc = 0; // never spiral after a long stall
  draw();
  const perf = window.__perf;
  if (perf) {
    perf.frameMs.push(performance.now() - t0);
    if (perf.frameMs.length > 600) perf.frameMs.shift();
  }
  requestAnimationFrame(frame);
}

requestAnimationFrame(frame);
window.__game.ready = true;
gameLog(`started seed=${seed}`);
