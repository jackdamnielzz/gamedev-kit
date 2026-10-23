---
name: godot
description: Godot 4 recipe for agent-built games - when to choose Godot over the web stack, working without the editor (headless import, tests, screenshots, exports), pixel-art project settings, 2D lights with normal maps, architecture with a deterministic GDScript sim, assets from Asset Forge and PixelLab, CI and Steam release, pitfalls.
when_to_use: Planning, scaffolding or building a game in Godot, choosing between Godot and the TypeScript web stack, or importing Asset Forge / PixelLab assets into Godot.
---

# Godot

Read `${CLAUDE_PLUGIN_ROOT}/docs/GODOT.md` before planning or changing a Godot project. The kit's principles in `GAME-STACK.md` still apply (specs, deterministic sim, content as data, tests and bots, reference-first art, the asset manifest).

Rules:

- The human does not need to use the Godot editor: write `.gd`, `.tscn`, `.tres` and `project.godot` as text, run Godot headless for import, tests and builds, and a normal run for screenshots.
- After copying assets in, run `godot --headless --path <project> --import` before running the game.
- Read every screenshot before calling visual work done.
- Keep game rules in pure `sim/` classes with one seeded RandomNumberGenerator; scenes only present state and send commands.
- Pin the Godot version and the console executable path in `docs/specs/000-stack.md`.
