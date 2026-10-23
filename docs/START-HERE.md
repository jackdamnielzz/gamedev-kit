# START HERE — briefing for every Claude session in a game project

This is the standing brief for any agent working in a game folder where the gamedev-kit plugin is enabled. The kit's SessionStart hook points every session here. Follow it before planning, designing or building anything.

## 1. Read before you start

**A new game, or a first session in a folder without `docs/specs/000-stack.md`.** Before you write any code, propose any stack, draft a concept or generate any asset, read these documents in full, in this order:

1. `START-HERE.md` (this file)
2. `GAME-STACK.md`: stack, architecture, repo layout, workflow, recipes per game type
3. `AI-ASSET-WORKFLOW.md`: the reference-first art pipeline, the animation decision guide, generators, cleanup, licences and Steam disclosure
4. `indie-game-development-guide.md`: lifecycle, scope, design, production, marketing
5. `STORY-AND-NARRATIVE.md`: story without text overload, storylet systems, pacing, text UX
6. `NANOGPT-API.md`: only the overview now; read the rest before the first generation call

Then reply to the human with a short brief, at most 10 lines: the rules you will follow, the questions you still need answered, and your recommended Claude model for the next step. Only then start.

**An existing game (the folder has `docs/specs/000-stack.md`).**

- Read the project's `CLAUDE.md`, `docs/concept.md` and every file in `docs/specs/` first. The project's decisions win over the kit.
- Before each task, read the kit sections that apply to it:
  - art and animation: `AI-ASSET-WORKFLOW.md`;
  - architecture, testing and tooling: `GAME-STACK.md`;
  - scope, release and marketing: the indie guide;
  - story, dialogue, events and narrative systems: `STORY-AND-NARRATIVE.md`.
- Re-read the full documents before a new asset group, a new major system, or a stack change.

Do not skim from memory. The documents change. The repo `jackdamnielzz/gamedev-kit` is the master copy, and the plugin's `docs/` folder holds the installed version of it.

## 2. Non-negotiable rules

1. **English for everything**: replies, code, comments, docs, in-game text, and every prompt for image, video, music or other AI tools.
2. **Model advice.** At the start of each task, say which Claude model fits it best: Opus for coordination, specs, art direction and judging comparisons; Sonnet for most building; Haiku for mechanical edits.
3. **Reference-first art.** Never build final art from a text description alone. Explore options with an image model, let the human pick, make reference sheets, then build (Blender, code, or the approved image itself), compare, and log. The full pipeline is in `AI-ASSET-WORKFLOW.md`; use `/gamedev-kit:new-asset <group>`.
4. **Choose the animation route on purpose.** Use the decision guide "Choosing an animation route" in `AI-ASSET-WORKFLOW.md`. In short:
   - an image model makes designs and variations, never the motion;
   - single-view characters are animated with an image-to-video model plus `art/py/video_to_sprites.py`;
   - small 32–64 px sprites come from PixelLab or Retro Diffusion;
   - units that need 8–32 facings or separate turrets come from 3D.
5. **Real pixel art only.**
   - Every generated or rendered pixel asset goes through scripted cleanup: one grid, one palette, binary alpha, a lint check. Then it gets a manual Sprite Grid pass (dithering off, no retro palette), and the lint runs again.
   - Never AI-upscale pixel art; scale with nearest-neighbour only.
   - Do not auto-snap an AI image that is already clean before the video step. It usually makes it worse; check it by eye instead.
6. **The human decides taste.** Batches of options, contact sheets and before/after images go to the human. The human picks reference sets and approves every hero asset and track. Never build on a first take nobody chose.
7. **Money.** Show the estimated cost before generation runs. Ask before going above the daily budget in `docs/specs/000-stack.md`. Pick the cheapest setting that is good enough. Example: 480p video is enough for sprites around 100 px tall; turn audio off.
8. **Log every AI asset** (references too) in `assets/manifest.json`: provider, model, prompt, date, cost, licence, `built_from`, `ai_pixels_shipped`. This feeds the Steam AI disclosure.
9. **Deterministic, testable game code.** Keep the sim and render layers separate. All content is data. Run tests and bot runs before reporting done. Read your own screenshots and previews before calling anything finished.
10. **Settings.** Game ideas and settings are not based on the Netherlands. Avoid real franchises' names and trademarks; describe looks in your own words, never "in the style of" a living artist or "like <existing game unit>".
11. **Never print or commit API keys.**
12. **Story lives in the verbs.** Tell the story through mechanics, the world and short reactive lines, not walls of text. Every line is short, never repeats and refers to something the player did; everything is skippable. Details and the checklist are in `STORY-AND-NARRATIVE.md`.

## 3. Where things are

| Need | Go to |
| --- | --- |
| Start a new game | `/gamedev-kit:new-game [title]` |
| A new group of art assets | `/gamedev-kit:new-asset <group>` |
| One-page concept | `/gamedev-kit:game-concept [idea]` |
| Stack choice | `/gamedev-kit:stack-advisor [question]` |
| Story, dialogue and event systems | `STORY-AND-NARRATIVE.md` (skill `gamedev-kit:story-design`) |
| Put a lesson back into the kit | `/gamedev-kit:sync-docs [change]` |
| Image, video and audio API calls | `NANOGPT-API.md`, `tools/gen_image.py` |
| Pixel-art generation (PixelLab) | `PIXELLAB-API.md`, `tools/gen_image.py --provider pixellab` |
| 3D props, 3D→pixel sprites, effects, Godot export (our own tool) | `ASSET-FORGE.md` (skill `gamedev-kit:asset-forge`) |
| Animation video to clean frames | `art/py/video_to_sprites.py` |
