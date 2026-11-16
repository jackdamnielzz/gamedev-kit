#!/usr/bin/env node
// Claude Code hook for game projects (wired up in .claude/settings.json, see GAME-STACK.md "Agent hooks").
//   pre  (PreToolUse on Edit|Write|MultiEdit): blocks edits to generated or engine-owned files.
//   post (PostToolUse on Edit|Write|MultiEdit): typechecks and lints an edited TypeScript file, and
//        validates data after a data/ JSON edit. Problems go back to Claude (exit code 2).
// Node only, no dependencies; works on Windows and Linux.
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

const mode = process.argv[2];
let input = {};
try {
  input = JSON.parse(readFileSync(0, "utf8") || "{}");
} catch {
  process.exit(0);
}
const root = process.env.CLAUDE_PROJECT_DIR || input.cwd || process.cwd();
const file = input.tool_input?.file_path || input.tool_input?.notebook_path;
if (!file) process.exit(0);
const rel = path.relative(root, path.resolve(root, file)).split(path.sep).join("/");
if (rel.startsWith("..")) process.exit(0);

function fail(message) {
  process.stderr.write(message.trim() + "\n");
  process.exit(2);
}

if (mode === "pre") {
  const blocked = [
    [/^public\/assets\//, "public/assets/ is generated: change the recipe or build script in art/, audio/ or tools/ and rebuild."],
    [/^\.godot\//, ".godot/ is Godot's cache: never edit it."],
    [/\.import$/, ".import files are written by Godot's importer: change the import settings in Godot or re-import."],
    [/^dist\//, "dist/ is build output: change the source and rebuild."],
  ];
  for (const [pattern, reason] of blocked) if (pattern.test(rel)) fail(`Blocked edit to ${rel}: ${reason}`);
  process.exit(0);
}

if (mode !== "post") process.exit(0);

const win = process.platform === "win32";
function run(cmd, args) {
  const r = spawnSync(cmd, args, { cwd: root, encoding: "utf8", shell: win, timeout: 110_000 });
  return { ok: r.status === 0, out: `${r.stdout || ""}${r.stderr || ""}`.trim() };
}
const head = (text, n = 40) => text.split("\n").slice(0, n).join("\n");
const hasPkg = existsSync(path.join(root, "package.json"));

if (hasPkg && /\.(ts|tsx|mts)$/.test(rel) && /^(src|tests)\//.test(rel)) {
  const problems = [];
  const tsc = run("npx", ["--no-install", "tsc", "--noEmit", "-p", "."]);
  if (!tsc.ok) problems.push(`Typecheck failed:\n${head(tsc.out)}`);
  const lint = run("npx", ["--no-install", "eslint", rel]);
  if (!lint.ok) problems.push(`ESLint failed for ${rel}:\n${head(lint.out)}`);
  if (problems.length) fail(problems.join("\n\n"));
}

if (hasPkg && /^data\/.*\.json$/.test(rel)) {
  const v = run("npm", ["run", "--silent", "validate"]);
  if (!v.ok) fail(`Data validation failed after editing ${rel}:\n${head(v.out)}`);
}

process.exit(0);
