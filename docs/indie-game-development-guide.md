# Indie Game Development: A Complete Guide

19 October 2026 · Niels

## 1. Introduction

Game development is the combined practice of design, software engineering, art, audio, production and business needed to turn an idea into a playable product that people buy or play. An indie game is one made without a large publisher's funding or control, usually by a solo developer or a team of 1–20 people who own their IP and make their own creative decisions.

Indie and AAA follow the same basic lifecycle. The difference is scale and risk: a AAA project has hundreds of specialists, budgets of tens to hundreds of millions and multi-year schedules, while an indie project has a few generalists, a budget from zero to a few hundred thousand euros, and 6 months to 5 years of development. Indies compensate with focus: a narrow scope, one strong hook, and a direct relationship with players.

| Aspect | Indie | AAA |
| --- | --- | --- |
| Team size | 1–20, mostly generalists | 100–1,000+, specialists |
| Budget | €0 – €500k typical | €20M – €300M+ |
| Development time | 6 months – 5 years | 3 – 7 years |
| Funding | Savings, side income, grants, small publishers, crowdfunding | Large publishers, platform holders |
| Engine | Off-the-shelf (Unity, Godot, Unreal, GameMaker) | Unreal or proprietary |
| Creative control | Full | Shared with publisher and stakeholders |
| Typical scope | One core mechanic, stylised art | Broad content, high-fidelity art |

This guide walks through the whole process: the market, the roles, every lifecycle phase, the technical foundations, art and audio pipelines, design craft, production, testing, business, marketing, release and post-launch. It closes with common pitfalls and a practical roadmap for a first commercial indie game.

## 2. The indie landscape in 2026

Indie games earn a large share of PC revenue, but the market is extremely top-heavy: roughly 20,000 games launched on Steam in 2025 and only about 300 earned more than $1 million.

| Metric (Steam, 2025) | Value | Source |
| --- | --- | --- |
| Games released | About 19,000–20,300 | KitGuru / SteamDB; VoxBooster |
| Total Steam game revenue (1 Jan – 19 Dec) | $17.7 billion | Game World Observer / Alinea Analytics |
| Indie share of that revenue | About 25% (about $4.4 billion) | Game World Observer / Alinea Analytics |
| Games earning > $1 million | About 300 | Notebookcheck |
| Games reaching 1,000 reviews | 608 (about 3%) | VoxBooster |
| Games with fewer than 10 reviews | About half | MP1st / SteamDB |
| Share earning < $1,000 (Gamalytic estimate) | About 66% | Yahoo Tech |

The biggest indie hits of 2025 were Schedule I (about $151M), R.E.P.O. (about $147M), PEAK (about $87M), Hollow Knight: Silksong (about $75M) and Escape from Duckov (about $53M), according to Alinea Analytics. Several of them were tiny teams whose games spread through streamers and co-op word of mouth.

What this means in practice:

- **Visibility, not access, is the bottleneck.** Anyone can publish on Steam for a $100 fee; getting seen is the hard part.
- **Many releases are hobby projects.** The low-revenue tail includes many first games and asset flips, so the odds for a well-scoped, well-marketed game are better than the raw numbers suggest.
- **Genre and hook matter more than polish alone.** Games that are fun to watch and share (co-op chaos, simulation, horror, roguelites) outperform.
- **AI-assisted releases are growing fast.** By mid-2026, roughly a third of new Steam releases carried an AI disclosure (see section 18), adding to the volume.

## 3. Roles and disciplines

Every game needs the same disciplines; on an indie team one person usually covers several of them, and anything nobody covers well is either outsourced, bought as assets, or designed around.

| Discipline | What it covers | Typical indie solution |
| --- | --- | --- |
| Game design | Rules, mechanics, systems, progression, balance, level design | The founder; often doubles as producer |
| Programming | Gameplay code, engine/tools, UI, AI, networking, platform integration, optimisation | The founder or a technical co-founder |
| Art | Concept art, characters, environments, animation, VFX, UI art | A co-founder artist, freelancers, or asset store packs |
| Technical art | Shaders, rendering setup, art pipeline tooling, performance of assets | Usually split between programmer and artist |
| Audio | Music, sound effects, mixing, implementation | Freelance composer and SFX libraries |
| Writing / narrative | Story, dialogue, lore, item text, localisation-ready strings | Designer, or a freelance writer |
| QA | Finding, reproducing and tracking bugs; regression and compatibility testing | The team plus community playtesters; QA agencies near launch |
| Production | Planning, scope, budget, milestones, keeping the team shipping | The founder, part-time |
| Marketing & community | Store page, trailers, social media, press, influencers, Discord | The founder, sometimes a publisher |
| Business & legal | Contracts, company, taxes, platform agreements, IP | The founder plus an accountant/lawyer as needed |
| Localisation | Translating and culturally adapting text and UI | Freelance translators or agencies, late in production |
| Porting | Bringing the game to consoles or other platforms | Specialised porting studios, often for a revenue share |

**Solo vs. small team.** Solo development gives full control and no salaries, but makes the developer a bottleneck on every discipline; successful solo games (Stardew Valley, Balatro, Schedule I) typically pick an art style the developer can produce alone. Small teams of 2–5 split mostly along code / art / design-plus-business, which is the most common shape for a commercially successful indie studio. Freelancers fill the gaps for music, trailers, translation and porting.

## 4. The development lifecycle at a glance

Nearly every game, indie or AAA, moves through the same nine phases; the two moments that decide a project's fate are proving the core loop is fun, and freezing features so the game can actually be finished.

Lifecycle (diagram in the original doc): 1 Concept → 2 Pre-production → 3 Prototyping → **Gate 1: the core loop is fun** → 4 Vertical slice → 5 Production → 6 Alpha → **Gate 2: features frozen, content locked** → 7 Beta → 8 Launch → 9 Post-launch.

The gates are the point of the structure: you only move to the vertical slice once a rough prototype is genuinely fun, and you stop adding features at alpha so beta can be spent finishing.

| Phase | Key question | Main output | Rough share of a 2-year indie project |
| --- | --- | --- | --- |
| 1 Concept | Is this idea worth exploring and can it sell? | One-page pitch, hook, comparable titles | 2–4 weeks |
| 2 Pre-production | What exactly are we making, and how? | Design pillars, scope document, tech choice, rough plan | 1–2 months (overlaps prototyping) |
| 3 Prototyping | Is the core mechanic fun? | Playable greybox prototypes | 1–3 months |
| 4 Vertical slice | Can we make it look, sound and feel like the final game? | One polished level or 10–20 minutes at final quality; pitch build | 2–4 months |
| 5 Production | Build everything | All levels, content, systems, art, audio | 9–14 months |
| 6 Alpha | Is everything in and playable end to end? | Feature-complete build | Milestone |
| 7 Beta | Is it stable, balanced and polished? | Content-complete build, bug fixing, optimisation | 2–4 months |
| 8 Launch | Is it ready to ship? | Release candidate / gold master, store page, marketing beats | 2–6 weeks |
| 9 Post-launch | How do we keep players and sales going? | Patches, updates, DLC, ports | Ongoing |

The phases overlap in practice, and marketing runs alongside from pre-production onward. Durations are rules of thumb, not a standard: small games may finish in 6 months, and many indie projects take 3–5 years. Sections 5–17 go through each phase and supporting discipline in detail.

## 5. Concept and pre-production

The goal of this phase is to choose an idea that is fun, feasible for your team and sellable, then write down just enough to keep everyone building the same game.

### 5.1 Ideation

- **Start from a hook, not a story.** A hook is one sentence that makes a player want to try it: "a deckbuilder where you play poker hands" (Balatro), "a co-op horror game where you loot a haunted mansion together" (R.E.P.O.).
- **Combine familiar with fresh.** A known genre plus one twist is easier to understand and market than something entirely new.
- **Use game jams.** Jams (Ludum Dare, GMTK Game Jam, Global Game Jam) force a playable idea in 48–72 hours and are a cheap way to test concepts. Many commercial indies started as jam games.
- **Play the genre deeply.** Know the top 10–20 games in your genre, what players praise and what they complain about in reviews.

### 5.2 Market validation

- Find 5–10 **comparable titles ("comps")** released in the last 3–5 years with similar scope and price.
- Estimate their sales with tools such as Gamalytic, VG Insights or SteamDB; a common rough rule is that lifetime units sold are 30–60× the number of Steam reviews.
- Check genre health: are new games in it still selling, or is it saturated?
- Ask whether your game is easy to show in a 5-second GIF or a 30-second clip. Visual clarity drives discovery on Steam, TikTok and YouTube.

### 5.3 Scoping

Scope is the number-one killer of indie projects. Estimate content as concrete counts (levels, enemies, items, minutes of play, lines of dialogue) and multiply your first time estimate by 2–3. A useful exercise is to define three versions:

| Version | Purpose |
| --- | --- |
| Minimum shippable game | The smallest version you would still be proud to sell |
| Target game | What you plan for |
| Dream game | Everything else; parked for updates, DLC or a sequel |

### 5.4 Design pillars

Pillars are 3–5 short statements that every feature must support, for example "every run feels different", "readable at a glance", "chaos with friends". When a feature does not serve a pillar, it gets cut. Pillars keep a small team aligned without heavy documentation.

### 5.5 The game design document (GDD)

Modern indie GDDs are living, short documents (often a wiki in Notion, Obsidian or Confluence) rather than 200-page specs. A typical structure:

1. One-page pitch: hook, genre, platform, target audience, comps, price point
2. Pillars and intended player experience
3. Core loop and secondary loops
4. Mechanics and systems (controls, rules, progression, economy)
5. Content list (levels, characters, items) with counts
6. Art and audio direction with reference boards
7. Technical overview: engine, target platforms, performance targets, risks
8. Scope, milestones and budget

### 5.6 Technical pre-production

Choose the engine and core tools (sections 7–8), set up version control and a build pipeline on day one, identify the riskiest technical problems (networking, procedural generation, large worlds, many units on screen) and spike them early with throwaway tests.

## 6. Prototyping and the vertical slice

Prototyping answers "is it fun?" as cheaply as possible; the vertical slice answers "can we make it good?" at final quality.

### 6.1 Prototyping principles

- **Test one question per prototype.** "Does dashing feel good?", "Is the economy interesting after 20 minutes?", "Do two players cause fun chaos?"
- **Greybox everything.** Use cubes, capsules, placeholder sprites and free sounds. Art before fun is wasted art.
- **Write throwaway code.** Prototype code is for learning; expect to rewrite the parts you keep.
- **Paper prototypes** work well for card games, strategy and economy systems: cards, dice and spreadsheets before code.
- **Time-box it.** Days to a few weeks per prototype. If a mechanic is not fun after honest iteration, change it or kill it.
- **Focus on game feel ("juice").** Input response, animation timing, screen shake, hit-stop, particles and sound often decide whether a mechanic feels fun.

### 6.2 Playtesting the prototype

Watch people play without explaining anything. Note where they get confused, bored or excited. Ask open questions afterwards ("What was the goal?", "When did you want to stop?") instead of "Did you like it?". Friends are polite; strangers on Discord, itch.io or at local meetups give more honest signal. Key signal: do testers ask to play again?

### 6.3 The vertical slice

A vertical slice is a short, complete, polished cut through the game: one level or 10–20 minutes that contains final-quality art, audio, UI, the core loop and representative progression. It:

- proves the art pipeline and the final look are achievable;
- gives a reliable baseline for estimating how long the rest of production will take (time per level, per enemy, per asset);
- becomes the pitch build for publishers and funds, and the basis for the first trailer and a Steam demo;
- surfaces technical problems (performance, tooling) before they are multiplied across the whole game.

After the slice, many teams do a **greenlight review**: go, change scope, or stop. Stopping here is cheap compared with stopping after a year of production.

## 7. Technical foundations

Almost every indie game today is built on an off-the-shelf engine; custom engines fell from over 70% of Steam releases in 2012 to about 13% in 2024 (Video Game Insights). The engine choice shapes your language, workflow, costs and target platforms.

### 7.1 Engine comparison (October 2026)

| Engine | Language(s) | Strengths | Weaknesses | Licence / cost | Share of 2024 Steam releases |
| --- | --- | --- | --- | --- | --- |
| Unity (6.x; 6.4 shipped March 2026) | C# | Huge ecosystem and Asset Store, strong 2D and 3D, best mobile and XR support, many tutorials | Closed source; 2023 Runtime Fee episode damaged trust (fee was cancelled in 2024) | Personal free up to $200k revenue and funding; Pro $2,310 per seat per year from 12 January 2026 | 51% |
| Unreal Engine (5.x) | C++, Blueprints (visual scripting) | Best-in-class 3D rendering (Nanite, Lumen), full source access, AAA tooling | Heavy hardware requirements, steep learning curve, weaker for 2D | Free; 5% royalty on lifetime gross revenue per product above $1M; Epic Games Store revenue royalty-free | 28% |
| Godot (4.7.2, August 2026) | GDScript (Python-like), C#, C++ via GDExtension | Free and open source (MIT), tiny download, excellent 2D, fast iteration, no royalties | Smaller ecosystem; console export requires third-party porting partners; 3D less mature | Free, no royalties | 5% |
| GameMaker | GML | Very fast for 2D, gentle learning curve, proven on hits (Undertale, Hyper Light Drifter) | 2D only in practice, proprietary | Free for non-commercial; paid licence for commercial and console exports | 4% |
| Frameworks (MonoGame, Bevy, LÖVE, Raylib, Phaser) | C#, Rust, Lua, C, JavaScript | Full control, light, great for programmers who like code-first | You build your own editor, tools and pipeline | Free, open source | Small |
| Custom engine | C++, Rust, etc. | Total control, can enable unusual tech (e.g. huge simulations) | Years of extra work; rarely worth it for a first game | Free but very costly in time | About 13% (mostly AAA) |

Shares from Video Game Insights' sample of 13,000+ Steam games (GameDev Reports). Unreal games earned 31% of Steam revenue in 2024 versus 26% for Unity, reflecting Unreal's use in larger projects.

**Rule of thumb:** 2D or small 3D game, solo or small team: Godot, Unity or GameMaker. High-fidelity 3D: Unreal. Mobile or XR: Unity. Browser game: Godot (web export), Phaser or plain TypeScript with a framework.

### 7.2 Core runtime concepts

**The game loop.** A game is a program that runs a loop dozens of times per second: read input, update the simulation, render a frame. Engines run this for you, but understanding it explains most bugs and performance problems.

```
while running:
    process_input()
    accumulator += frame_time
    while accumulator >= FIXED_DT:     # fixed timestep for physics/simulation
        update_simulation(FIXED_DT)
        accumulator -= FIXED_DT
    render(interpolation = accumulator / FIXED_DT)
```

- **Frame budget:** at 60 FPS you have 16.7 ms per frame for everything; at 30 FPS, 33.3 ms.
- **Variable vs. fixed timestep:** rendering and animation use the real frame time (delta time); physics and deterministic simulations (strategy, networking) use a fixed step so results are reproducible.

**Architecture patterns.**

| Pattern | What it is | Where you meet it |
| --- | --- | --- |
| Scene graph / node tree | Objects arranged in a parent-child hierarchy with transforms | Godot nodes, Unity GameObjects, Unreal Actors |
| Component-based design | Behaviour built from reusable components attached to objects | Unity MonoBehaviours, Unreal ActorComponents |
| Entity Component System (ECS) | Entities are IDs, components are plain data, systems process all entities with certain components; cache-friendly and fast | Unity DOTS, Bevy, Flecs, custom engines for many-unit simulations |
| State machine | An object is in exactly one state (idle, run, jump) with defined transitions | Player controllers, enemy AI, UI flows, animation |
| Observer / events / signals | Objects broadcast events; others subscribe, reducing coupling | Godot signals, C# events, Unreal delegates |
| Command pattern | Actions stored as objects; enables undo, replays, input remapping, networking | Strategy and puzzle games, level editors |
| Object pooling | Reusing objects instead of creating/destroying them to avoid garbage-collection spikes | Bullets, particles, enemies |
| Data-driven design | Gameplay values and content in data files (JSON, ScriptableObjects, Resources, spreadsheets) instead of code | Balancing, items, levels, localisation |

**Key subsystems.**

- **Rendering:** sprites and tilemaps (2D); meshes, materials, shaders, lighting, shadows and post-processing (3D). Main performance levers: draw calls/batching, overdraw, texture size, shader complexity, level of detail (LOD) and culling.
- **Physics:** collision detection (shapes, layers, triggers) and rigid-body simulation. Many 2D games use simple kinematic movement instead of full physics for tighter control.
- **Input:** abstract actions ("jump") mapped to devices (keyboard, gamepad, touch); support rebinding and multiple controllers from the start.
- **Animation:** sprite sheets, skeletal animation (Spine, DragonBones, engine rigs), blend trees, inverse kinematics and procedural animation.
- **AI:** finite state machines, behaviour trees, utility AI, goal-oriented action planning (GOAP), and pathfinding (A*, navigation meshes, flow fields for large unit counts).
- **UI:** menus, HUD, inventory; engines provide UI systems (Unity UI Toolkit, Godot Control nodes, Unreal UMG). UI usually takes far longer than expected.
- **Save systems:** serialise game state to JSON or binary; version your save format so updates do not break old saves; support Steam Cloud.
- **Audio engine:** playback, 3D positioning, mixing buses, dynamic music (section 10).
- **Procedural generation:** noise (Perlin/Simplex), wave function collapse, cellular automata, seeded random generators for reproducible worlds.
- **Networking (multiplayer):** client-server vs. peer-to-peer; authoritative servers; state synchronisation vs. deterministic lockstep (common in RTS); lag compensation, client-side prediction and rollback (fighting games). Tools include Steamworks networking, Netcode for GameObjects/Mirror/FishNet (Unity), Godot's high-level multiplayer API, Unreal replication, and services such as Photon, Epic Online Services and Steam relay. Multiplayer often doubles development and testing effort; decide early.

### 7.3 Performance targets

Define minimum and recommended hardware early (for PC: a Steam Deck is a good minimum target in 2026). Profile on low-end hardware regularly, not only at the end.

## 8. Languages, tools and pipelines

The tooling around the engine (version control, builds, asset pipelines, task tracking) decides how fast and safely a team can iterate; set it up in the first week, not before launch.

### 8.1 Programming languages

| Language | Used with | Notes |
| --- | --- | --- |
| C# | Unity, Godot (.NET), MonoGame, Stride | Most common indie language; garbage-collected, productive |
| C++ | Unreal, custom engines, Godot GDExtension | Maximum performance and control; slower to write and debug |
| GDScript | Godot | Python-like, tightly integrated, fast iteration |
| Blueprints | Unreal | Visual scripting; good for designers, prototyping and glue logic |
| GML | GameMaker | Simple scripting for 2D |
| Rust | Bevy, custom engines | Memory safety and performance; young ecosystem |
| Lua | LÖVE, Defold, modding layers | Lightweight, often embedded for modding and scripting |
| JavaScript / TypeScript | Phaser, PixiJS, Three.js, Babylon.js | Browser games; easy distribution |
| HLSL / GLSL / shader graphs | All engines | Shaders for visual effects and rendering |

### 8.2 Version control

Version control is non-negotiable, even for solo developers: it is your backup, history and collaboration tool.

- **Git + Git LFS** (GitHub, GitLab, Bitbucket, Azure DevOps): standard for code; LFS stores large binaries (textures, audio, models). Use an engine-specific .gitignore.
- **Perforce Helix Core:** industry standard for large binary-heavy projects and Unreal teams; supports file locking.
- **Unity Version Control (Plastic SCM):** integrated with Unity; cloud seat charges were removed in Q1 2026.
- Binary files (scenes, prefabs, .uasset) cannot be merged: agree who owns which file, use file locking, and split levels into smaller scenes or sub-levels.

### 8.3 Builds and CI/CD

- Automate builds for every target platform (Windows, macOS, Linux/Steam Deck, web, consoles) with GitHub Actions, GitLab CI, Jenkins, TeamCity, Unity Build Automation, or tools like GameCI.
- Run automated tests (unit tests on game logic, smoke tests that load every level) on each commit.
- Upload builds automatically to Steam branches (SteamPipe / steamcmd) or itch.io (butler) so testers always have the latest version.
- Use semantic version numbers and keep a changelog; it pays off for patch notes later.

### 8.4 Asset pipeline

The asset pipeline is the route from a source file (a .psd, .aseprite, .blend, .wav) to an optimised in-game asset.

1. Artists keep source files in a defined folder structure and naming convention.
2. Export with consistent settings (scale, pivot, frame rate, colour space, compression).
3. The engine imports and converts them (texture compression, mesh optimisation, audio encoding).
4. Automate repetitive steps with scripts or engine import presets.
5. Track asset status (placeholder, work in progress, final) so placeholders do not ship.

### 8.5 Supporting tools

| Need | Common tools |
| --- | --- |
| Code editor / IDE | Visual Studio, JetBrains Rider, VS Code |
| Task tracking | Trello, Notion, Jira, Linear, Codecks (built for game dev), HacknPlan |
| Documentation / GDD | Notion, Obsidian, Confluence, Miro for boards |
| Bug and crash reporting | Sentry, Backtrace, BugSplat, Unity Cloud Diagnostics, in-game feedback forms |
| Analytics | GameAnalytics, Unity Analytics, custom telemetry (with GDPR-compliant consent) |
| Communication | Discord, Slack |
| Localisation management | Crowdin, Lokalise, POEditor, spreadsheets for small games |
| Dialogue and narrative | Ink, Yarn Spinner, Dialogic (Godot), articy:draft |

## 9. Art and animation pipeline

For indies, a coherent art style matters far more than technical fidelity: pick a style the team can produce consistently at the required volume, and that reads clearly in a small Steam capsule and a 5-second clip.

### 9.1 Art direction

- Build mood boards and a style guide (palette, line weight, lighting, proportions, UI style) during pre-production.
- Prioritise **readability**: players must instantly distinguish player, enemies, hazards, pickups and interactive objects (silhouette, contrast, colour coding).
- Common indie-friendly styles: pixel art, low-poly 3D, flat/vector 2D, hand-drawn, cel-shaded, voxel, minimalist.

### 9.2 2D pipeline

| Step | Tools |
| --- | --- |
| Concept and sketches | Krita, Photoshop, Clip Studio Paint, Procreate |
| Pixel art and sprite animation | Aseprite, Pyxel Edit, Pixelorama |
| Vector / illustrated art | Affinity Designer, Illustrator, Inkscape |
| Skeletal 2D animation | Spine, DragonBones, engine-native 2D rigs |
| Tilesets and level art | Tiled, LDtk, engine tilemap editors |
| Packing | Texture atlases / sprite sheets to reduce draw calls |

Pixel art details: choose a base resolution early (e.g. 320×180 or 640×360 scaled to 1080p/4K by integer factors), use a consistent pixel density, and configure the engine for point filtering and pixel-perfect cameras.

### 9.3 3D pipeline

1. **Concept art** and orthographic reference sheets.
2. **Modelling** in Blender (free, industry-wide in indie), Maya or 3ds Max; sculpting in ZBrush or Blender for high detail.
3. **Retopology and UV unwrapping** for clean, game-ready meshes with a sensible polygon budget.
4. **Texturing** with Substance Painter/Designer, Blender or Quixel; physically based rendering (PBR) maps: albedo, normal, roughness, metallic, ambient occlusion.
5. **Rigging and skinning:** a skeleton bound to the mesh.
6. **Animation:** hand-keyed, motion capture (including low-cost video-based mocap), or libraries such as Mixamo.
7. **Export** (FBX, glTF) and engine import with LODs, collision meshes and materials.

### 9.4 VFX, lighting and technical art

- **VFX:** particle systems (Unity VFX Graph / Shuriken, Unreal Niagara, Godot GPUParticles), flipbook textures, shader effects (dissolve, outlines, water).
- **Lighting:** baked lightmaps for static scenes (cheap at runtime), dynamic lights for moving objects; post-processing (bloom, colour grading, vignette) defines much of the final mood.
- **Technical art** bridges art and code: shaders, tools, import automation, performance budgets per asset.

### 9.5 UI and UX art

UI needs its own style guide: fonts (check licences for commercial and in-game use), icon set, button states, and layouts that scale from Steam Deck (1280×800) to 4K and work with gamepad navigation.

### 9.6 Buying vs. making assets

Asset stores (Unity Asset Store, Fab for Unreal, itch.io, Kenney's free packs) save enormous time on props, VFX, sound and tools. Risks: an inconsistent look, and players recognising "asset flips". Use assets for invisible or generic parts, and make the hero assets (characters, key art, signature environments) yourself or commission them.

## 10. Audio

Audio is roughly half of how a game feels, yet it is often added last; plan it from the vertical slice onward and budget for at least a freelance composer and a sound pass.

- **Music:** composed in a DAW (Ableton Live, FL Studio, Logic Pro, Reaper, Cubase). Options: a freelance composer (flat fee or fee plus soundtrack revenue share), licensed libraries, or your own work. Agree in writing who owns the music and whether you may sell the soundtrack.
- **Adaptive music:** layers or stems that change with gameplay intensity, horizontal re-sequencing between sections, stingers for events.
- **Sound effects (SFX):** recorded foley, synthesised sounds (e.g. sfxr/jsfxr for retro), or commercial libraries (Sonniss GDC bundles are free each year, Soundly, Boom Library). Layer and vary pitch and volume randomly to avoid repetition.
- **Voice-over:** expensive and hard to change late; many indies use partial VO, grunts or text-only dialogue. Check union rules and contracts (and AI-voice clauses) when hiring actors.
- **Middleware:** FMOD and Wwise give sound designers their own tool for adaptive audio, mixing and parameters; both are free for small-budget indies under their indie licences. Engine-native audio is sufficient for many small games.
- **Mixing:** use buses (music, SFX, UI, voice), ducking, a master limiter, and separate volume sliders in the options menu. Test on cheap headphones, laptop speakers and a TV.
- **Accessibility:** subtitles with speaker names, visual indicators for important sounds, mono audio option.

## 11. Game design craft

Good game design is the deliberate shaping of what the player does, feels and decides from second to second and hour to hour; it is refined almost entirely through iteration and playtesting.

### 11.1 Loops

- **Core loop** (seconds to minutes): the action the player repeats most, such as jump-shoot-dodge, or plant-water-harvest.
- **Secondary loop** (minutes to an hour): runs, levels, days, matches; each one feeds resources and goals back into the core loop.
- **Meta loop** (hours to weeks): long-term progression, unlocks, collections, story.

Example core loop (roguelite, diagram in the original doc): Play a run (fight, explore, make choices) → Earn rewards (gold, experience, unlocks) → Upgrade (buy perks, open new options) → Return stronger (harder runs, new goals) → back to Play a run.

Every step in the loop should produce a reason to take the next one; if a player can skip a step without loss, it is not part of the loop.

### 11.2 Mechanics, dynamics and aesthetics

The MDA framework (Hunicke, LeBlanc, Zubek) is a useful lens: designers write **mechanics** (rules), which produce **dynamics** (behaviour during play), which create **aesthetics** (the emotional experience: challenge, discovery, fellowship, expression). Design from the feeling you want backwards to the rules that produce it.

### 11.3 Key design areas

| Area | What to get right |
| --- | --- |
| Game feel | Responsive controls, coyote time and input buffering in platformers, camera smoothing, feedback on every action |
| Difficulty and flow | Challenge that rises with skill (flow channel); difficulty options; teach, test, then twist each mechanic |
| Onboarding | Teach through play, not text; introduce one idea at a time; the first 5–15 minutes decide Steam refunds (2 hours / 14 days rule) |
| Level design | Greybox first; guide with light, landmarks and composition; pacing of tension and release; optional secrets |
| Systems and economy | Sources and sinks of resources; avoid dominant strategies; model in spreadsheets or simulations |
| Balancing | Data-driven values, playtest telemetry, spreadsheets; balance last, after mechanics are stable |
| Progression | Clear short- and long-term goals; meaningful choices over raw stat increases |
| Narrative | Environmental storytelling, emergent stories from systems, branching dialogue (Ink, Yarn Spinner); scope writing like any other content |
| Replayability | Procedural generation, randomised runs, multiple builds or endings, challenge modes, modding support |
| UX and UI | Clear information hierarchy; consistent controls; readable at Steam Deck size; full gamepad support |

### 11.4 Accessibility

Accessibility widens your audience and is increasingly expected. Cheap wins: remappable controls, subtitles with size options, colour-blind-safe palettes or filters, adjustable difficulty or assist modes, hold-vs-toggle options, screen shake and flash toggles, and readable UI scaling. See the Game Accessibility Guidelines (gameaccessibilityguidelines.com) for a full checklist.

## 12. Production and project management

Production is the discipline of actually finishing: controlling scope, sequencing work, and keeping a small team healthy over a long project.

### 12.1 Planning approach

- **Milestones** give the project a backbone: prototype, vertical slice, demo, alpha, beta, release candidate, launch. Each has concrete exit criteria ("all 30 levels playable start to end").
- **Agile-style iteration** works well for games: 1–2-week sprints, a prioritised backlog, short weekly reviews of a playable build. Scrum ceremonies can be lighter for 1–3 people.
- **Kanban boards** (to do / doing / review / done) suit solo developers and small teams.
- **Feature priority:** label everything Must / Should / Could / Won't (MoSCoW) and cut from the bottom when time runs short.

### 12.2 Estimating and scope control

- Estimate from the vertical slice: if one level took 3 weeks at final quality, 20 levels take 60 weeks unless you build tools or reuse content.
- Add a 20–30% buffer for polish, bugs, platform requirements and the unknown; first-time teams usually need more.
- Watch for **feature creep**: every new idea goes into a "later" list, not into the current sprint.
- Build **tools that multiply content** (level editors, procedural systems, data-driven enemies) when the game needs a lot of content.

### 12.3 Budgeting

A simple indie budget lists: team time (even unpaid founder time has an opportunity cost), freelancers (music, art, trailer, translation, porting), software licences, hardware and devkits, marketing (events, ads, key art, trailer), legal and accounting, QA, platform fees, and a 10–20% contingency. Monthly burn rate × planned months = the runway you need.

### 12.4 Sustainable pace

Crunch (sustained overtime) causes burnout, bugs and abandoned projects, and is a leading reason indie developers quit. Keep regular hours, ship small milestones to stay motivated, keep a done-list, and protect family time; plan the schedule so the final months are not the hardest. Many successful indies started part-time alongside a job and only went full-time after a funded or proven project.

## 13. QA, testing and optimisation

Quality assurance runs through the whole project, not just the end: playtesting checks whether the game is good, bug testing checks whether it works, and profiling checks whether it runs well.

### 13.1 Types of testing

| Type | Purpose | When |
| --- | --- | --- |
| Playtesting | Is it fun, clear, well paced? | From the first prototype, every milestone |
| Functional / bug testing | Does everything work as designed? | Continuously; intensive in beta |
| Regression testing | Did a fix break something else? | After every significant change; automate where possible |
| Automated tests | Unit tests for logic, integration and smoke tests that load levels or run bots | On every commit via CI |
| Compatibility testing | Different GPUs, resolutions, controllers, OS versions, Steam Deck | Beta, before launch |
| Performance testing | Frame rate, memory, loading times on minimum spec | From the vertical slice onward |
| Localisation QA | Text overflow, missing strings, cultural issues, fonts for all scripts | After translation |
| Certification / compliance | Platform-holder requirements (Sony TRCs, Xbox XRs, Nintendo lotcheck), Steam Deck Verified review | Before console and Deck releases |

### 13.2 Bug tracking

Every bug report needs: steps to reproduce, expected vs. actual result, build version, platform, severity (crash / blocker / major / minor / cosmetic) and attachments (screenshots, logs, save file). Use an issue tracker (GitHub Issues, Jira, Codecks), an in-game bug-report button that attaches logs automatically, and crash reporting (Sentry, Backtrace).

### 13.3 External playtests

- Steam Playtest (a free, separate app for sign-up playtests), closed beta branches with keys, itch.io builds, and Discord testers.
- Record sessions (with permission), use short surveys, and collect telemetry such as where players die or quit.
- Steam demos and Next Fest double as large-scale playtests (section 15).

### 13.4 Optimisation

1. **Measure first** with profilers: Unity Profiler and Frame Debugger, Unreal Insights, Godot's profiler and monitors, RenderDoc, PIX, Superluminal.
2. Find out whether you are **CPU-bound** (game logic, physics, draw-call submission) or **GPU-bound** (shaders, overdraw, resolution, post-processing).
3. Common fixes: batching and atlasing, object pooling, LODs and culling, fewer real-time lights, texture compression, spreading expensive work across frames, avoiding per-frame memory allocation (garbage-collection spikes), and moving hot code to faster paths (jobs, compute shaders, native code).
4. Re-test on minimum-spec hardware after each optimisation.

## 14. The business side

Most indie games are funded by the developers themselves; outside money (publishers, grants, investors, crowdfunding) usually becomes realistic only once a convincing vertical slice or demo exists.

### 14.1 Funding options

| Source | How it works | Pros | Cons |
| --- | --- | --- | --- |
| Self-funding | Savings, a day job, freelance work, a partner's income | Full ownership and control | Slow; personal financial risk |
| Publisher | Advance for development and/or marketing, recouped from revenue; then a revenue split | Money, marketing, QA, porting, platform contacts | Gives up revenue share and sometimes rights; recoup can take years |
| Grants and public funds | Non-repayable or partly repayable money from cultural or innovation funds | Keeps ownership | Competitive, paperwork, criteria (cultural value, innovation) |
| Crowdfunding | Kickstarter, Backerkit, Gamefound; pre-sales to an existing community | Validates demand, builds community | Needs an existing audience; fulfilment obligations; failed campaigns hurt |
| Early Access | Sell an unfinished game and develop it with player feedback | Revenue during development | Launch visibility spent early; players expect steady updates |
| Investors / VC | Equity investment in the studio | Larger budgets | Dilution; pressure for growth; rare for first games |
| Platform deals | Exclusivity or subscription deals (Game Pass, PlayStation Plus, Epic) | Guaranteed money | Limited availability; negotiation power needed |

**Publisher deals in numbers.** In a sample of 30 contracts analysed by games lawyer Kellen Voyer, the average advance was about $318,000 and the publisher took 60% of revenue while recouping it. Voyer Law's larger 2025 analysis of 100+ deals found an average developer revenue share of 57.7%, ranging from 50% to 85%. Watch these terms more than the headline split: what is recoupable (marketing? localisation?), whether you keep the IP (license, never assign), the term (typically 5–7 years), sequel options, platform rights, and what reverts to you if the publisher folds.

### 14.2 Funding in the Netherlands

| Fund / incentive | What it offers |
| --- | --- |
| Creative Industries Fund NL (Stimuleringsfonds Creatieve Industrie) | Grant schemes and open calls for digital culture and games, including a games professionalisation call (not for direct production) |
| Immerse\Interact (Creative Industries Fund NL with the Netherlands Film Fund) | Support for interactive and immersive works, including games |
| WBSO | Dutch tax incentive for R&D work, usable for technically innovative development |
| MIT-regeling and regional development funds (e.g. Oost NL) | Innovation subsidies and investment for SMEs |
| Creative Europe MEDIA | EU support for the development of innovative, narrative video games |
| Midgame Fund, Indie Fund and other investors | Early-stage investment for game studios |

The Dutch Games Industry funds overview (dutchgamesindustry.nl/funds) keeps a current list; Dutch Game Garden and the Dutch Games Association are useful for networking and incubation.

### 14.3 Company, legal and IP

- **Company form:** many start as a sole proprietorship (eenmanszaak) and move to a private limited company (BV) once revenue or liability grows, or when sharing ownership with co-founders.
- **Co-founder agreement:** write down ownership split, roles, vesting, IP assignment, and what happens if someone leaves, before you start. This prevents the most common indie studio disputes.
- **Contracts with freelancers:** make sure IP is transferred to your company in writing (work-for-hire / IP transfer clause), including music and art.
- **Licences:** check engine, font, asset, music and middleware licences for commercial use and console distribution.
- **Trademarks:** search the game name before announcing; consider registering it (EUIPO/BOIP) once the name is final.
- **Privacy and consumer law:** GDPR for analytics, accounts and newsletters; EU consumer rules for in-game purchases and loot boxes; age ratings (PEGI, ESRB, IARC for digital storefronts).
- **Taxes:** VAT on digital sales is usually handled by the storefront in the EU; you still declare income, and you may need a W-8BEN-E form for US tax withholding on Steam income.

This section is general information, not legal or financial advice; consult a lawyer or accountant for contracts and company setup.

## 15. Marketing and community

Marketing starts in pre-production, not at launch: on Steam, the main goal before release is collecting wishlists, because wishlisters are notified at launch and wishlist velocity feeds Steam's recommendation algorithm.

### 15.1 Marketing timeline

| When | What to do |
| --- | --- |
| Concept / prototype | Choose a marketable hook; post development GIFs; start a devlog, a mailing list and a Discord |
| Vertical slice (12–24 months before launch) | Launch the Steam "Coming Soon" page with capsule art, a trailer and screenshots; announce the game |
| Production | Regular social posts (TikTok, YouTube Shorts, Reddit, X, Bluesky), genre and online festivals, press and streamer outreach |
| 3–9 months before launch | Public demo; Steam Next Fest (one per game, ever) |
| 1–2 months before | Release date announcement, launch trailer, press kit, review keys to press and creators |
| Launch week | Launch discount (often 10–20%), streams, community engagement, fast patches |
| After launch | Seasonal sales, updates, DLC, bundles, ports |

### 15.2 The Steam store page

- **Capsule art** is the most important marketing asset: readable at thumbnail size, clear genre, the game's name legible. Commission a professional if you can.
- **Trailer:** gameplay in the first 3–5 seconds, no long logos; 30–90 seconds.
- **Screenshots and GIFs:** show the actual gameplay loop; the first 4 screenshots matter most.
- **Short description and tags:** state genre and hook plainly; use tags that match how players search.

### 15.3 Steam Next Fest and wishlists

Next Fest is a week-long demo festival held three times a year; in 2026 the editions run February 23 – March 2, June 15–22 and October 19–26 (the last one running this week as of writing). It mostly multiplies momentum a game already has:

- The February 2026 edition had more than 3,500 demos. The median demo in Chris Zukowski's developer survey gained 806 wishlists during the fest, while GameDiscoverCo's estimate across all demos is nearer 200.
- Pre-fest wishlists strongly predict fest results; around 2,000 wishlists is often cited as the point where the fest starts paying off.
- Common benchmarks: 7,000–10,000 wishlists at launch is a reasonable target for a modest commercial release; tens of thousands give a good chance of featuring in Steam's "Popular Upcoming" list.
- Conversion varies by genre and freshness: one 2026 analysis puts the median at about 12% of wishlists converting to day-1 sales, while GameDiscoverCo found a median first-week ratio of 0.15× for games with 25,000+ wishlists.

### 15.4 Channels that work for indies

- **Streamers and YouTubers:** the strongest discovery channel in 2025; games that are fun to watch (co-op chaos, horror, simulation, surprising mechanics) spread through creators. Use Keymailer, Lurkit or direct emails with keys.
- **Short-form video:** TikTok, Shorts and Reels with a hook in the first second.
- **Reddit and genre communities:** honest devlog posts in subreddits such as r/IndieGaming or genre-specific communities; follow each community's rules.
- **Festivals and events:** online festivals (genre fests, Steam themed fests), physical shows (Gamescom, PAX, Day of the Devs; in the Netherlands, Indigo and Dutch Game Garden events).
- **Press:** a press kit (presskit() or a simple page) with logo, art, trailer and a fact sheet; smaller sites and newsletters are more reachable than large outlets.
- **Discord and mailing list:** your most loyal players; use them for playtests, feedback and launch-day momentum.
- **Paid ads:** rarely profitable for premium PC indies, more common in mobile.

Useful resources: Chris Zukowski's How To Market A Game (howtomarketagame.com), Simon Carless's GameDiscoverCo newsletter, and Steamworks documentation on visibility.

## 16. Platforms and release

For most indie games, Steam on PC is the primary launch platform, with consoles, mobile or other stores added later once the game has proven itself; the launch itself is a planned, multi-week operation rather than a single button press.

### 16.1 Platform overview

| Platform | Entry requirements | Store fee (standard) | Notes |
| --- | --- | --- | --- |
| Steam (PC, Steam Deck) | $100 app fee per game (recouped after $1,000 in revenue) | 30%; 25% above $10M; 20% above $50M per game | Largest PC store; wishlists, Next Fest, demos, Early Access, Steam Deck Verified |
| Epic Games Store | Application and review | 12% | Unreal royalty waived on Epic Store revenue |
| itch.io | Free | Developer chooses (default 10%) | Great for jams, prototypes, demos and niche audiences; small sales volume |
| GOG | Curated | 30% (varies) | DRM-free audience; selective |
| Consoles (PlayStation, Xbox, Switch 2) | Developer programme approval, devkits, platform certification, age ratings | Typically 30% | Often handled by a publisher or porting studio; Godot requires third-party porting for consoles |
| Mobile (App Store, Google Play) | Developer accounts (annual or one-off fee) | 15% for small developers under $1M per year; 30% standard | Different business models (free-to-play, ads, in-app purchases); touch controls; very crowded |
| Web (browser) | Hosting or portals (CrazyGames, Poki, itch.io) | Ad revenue share | Instant play; good for small games and marketing demos |

Fee figures reflect platform terms as generally published; check each platform's current developer agreement before relying on them.

### 16.2 Pricing

Price relative to comparable games, not development cost. Typical premium indie prices are $5–$30; most successful small-to-mid indies sit around $10–$20. Players accept higher prices for more content and replayability. Steam regional pricing is suggested automatically; launch discounts of 10–20% are common. Remember Steam's refund policy: players can refund within 14 days if they have played under 2 hours, so the first two hours must deliver.

### 16.3 Early Access

Early Access lets you sell an unfinished game. It suits systemic, replayable games (survival, roguelites, colony sims, sandbox) that benefit from community feedback, and it is risky for narrative or linear games. Have a stable, fun core and a public roadmap, and update regularly; abandoned Early Access games damage trust.

### 16.4 Launch checklist

1. Release candidate build passes QA on all target hardware, including Steam Deck.
2. Store page final: capsule art, trailer, screenshots, description, tags, system requirements, AI disclosure, age rating, price.
3. Steamworks setup: achievements, cloud saves, controller configuration, depots and branches, launch discount scheduled.
4. Press kit online; review keys sent 1–2 weeks before launch with an embargo.
5. Release date chosen to avoid major releases in the same genre and big Steam sales; many indies launch Tuesday to Thursday.
6. Community ready: Discord announcements, mailing list, social posts, launch stream.
7. Team available for hotfixes during launch week; monitoring crash reports and reviews.
8. Day-one patch and the first update planned, not improvised.

## 17. Post-launch

Launch is the start of a game's commercial life, not the end: most premium indie games earn a large share of their lifetime revenue after launch week through updates, sales, DLC and ports.

- **Hotfixes and patches:** fix crashes and blockers within days; keep patch notes clear and frequent in the first month.
- **Listen to reviews:** Steam review score ("Very Positive" and up) strongly affects visibility and conversion; address recurring complaints quickly.
- **Content updates:** free updates bring lapsed players back, trigger Steam update visibility and often generate review and sales spikes.
- **Sales calendar:** participate in Steam seasonal sales (Spring, Summer, Autumn, Winter) and themed fests; deeper discounts over time; bundles with similar indies.
- **DLC and expansions:** paid content once the base game has an engaged audience; soundtrack and supporter-pack DLCs are low-effort extras.
- **Ports:** consoles and mobile, often through a porting studio for a fee or revenue share, can double a successful game's lifetime revenue.
- **Localisation:** adding Simplified Chinese, Japanese, Korean, German, French, Spanish, Brazilian Portuguese and Russian often expands reach significantly; Chinese is frequently the biggest non-English Steam market for indies.
- **Modding and community content:** Steam Workshop, level editors and mod support extend lifespan.
- **Analytics:** track retention (where players stop), completion, popular builds or modes; use it to guide updates (with GDPR-compliant consent).
- **Live ops** (seasons, events, battle passes) are mainly relevant for multiplayer and free-to-play games and require ongoing staffing.
- **Post-mortem:** write down what worked and what did not; it is the most valuable input for your next game.

## 18. AI in game development (2026)

AI tools are now part of everyday indie development, mostly as productivity aids; what players see is regulated by store disclosure rules and judged by a vocal part of the audience.

### 18.1 Where AI is used

| Area | Typical uses | Caveats |
| --- | --- | --- |
| Programming | Coding assistants, refactoring, writing tests, explaining engine APIs, debugging | Review all code; assistants can produce subtle bugs and engine-version mismatches |
| Design and writing | Brainstorming, item and flavour text drafts, balancing spreadsheets, documentation | Generic output; keep a human voice for story and dialogue |
| Art | Concept exploration, mood boards, texture variations, upscaling | Player-facing generated art requires disclosure on Steam and often draws backlash; style consistency issues |
| Audio | Placeholder music, SFX generation, voice prototyping | Voice-actor and union rules; disclosure for shipped content |
| QA and tooling | Automated playtesting bots, log analysis, localisation drafts | Translations still need native review |
| In-game AI features | Live-generated dialogue or content | Requires guardrails against illegal output and in-game reporting on Steam |

### 18.2 Steam's disclosure rules

Valve has required AI disclosure since January 2024 and rewrote the form on 17 January 2026:

- Behind-the-scenes efficiency tools, such as coding assistants, are explicitly exempt.
- Pre-generated content that players see or hear (art, audio, text, voice), including marketing assets on the store page, must be disclosed; the note appears on the store page.
- Games that generate content live during play must describe their guardrails, and Steam lets players report problematic output through the overlay.

Adoption is rising fast: a census of about 53,600 releases estimates that roughly one in three new Steam games carried a disclosure by mid-2026. Google Play's AI-content labelling rules became enforceable on 15 April 2026.

### 18.3 Practical advice

- Use AI freely for productivity; be deliberate about anything that ships to players.
- Be honest in disclosures; non-disclosure can breach the Steam Distribution Agreement.
- Check ownership: in many jurisdictions, purely machine-generated content may not be protected by copyright, which weakens your IP; human-authored or substantially edited work is safer.
- Expect community scrutiny, especially for art and voice; a distinctive human-made art style is also a marketing asset.

## 19. Pitfalls and a roadmap for a first indie game

Most indie projects fail for the same few reasons, and nearly all of them are about scope and marketing rather than technical skill.

### 19.1 Common pitfalls

| Pitfall | Why it hurts | Prevention |
| --- | --- | --- |
| Scope too big | Projects never finish or burn out the team | Make small games first; define a minimum shippable game; cut features early |
| No validation | Years spent on a game nobody searches for | Check comps and genre health; test the hook with GIFs and a store page early |
| Marketing too late | Launch with a few hundred wishlists and no visibility | Store page 12+ months before launch; post consistently; build a mailing list |
| Polishing before the fun is found | Wasted art and code | Greybox prototypes; gate 1 before the vertical slice |
| Endless feature creep | The finish line keeps moving | Feature freeze at alpha; a "later" list |
| Weak capsule art and trailer | Low click-through on Steam | Invest in key art; show gameplay in the first seconds |
| Rewriting the engine or building tools forever | No game progress | Use an off-the-shelf engine; build tools only for proven needs |
| No version control or backups | Lost work, broken builds | Git or Perforce from day one; offsite backups |
| Ignoring performance until the end | A painful final optimisation crunch | Profile regularly on minimum-spec hardware |
| Unclear agreements with collaborators | Disputes over ownership and money | Written co-founder and freelancer contracts with IP transfer |
| Burnout and crunch | Health problems and abandoned projects | Sustainable hours, small milestones, part-time start |

### 19.2 A practical roadmap

1. **Learn the engine (1–3 months):** follow official tutorials, then rebuild 2–3 tiny classic games (Pong, Breakout, a platformer level) without a tutorial.
2. **Join 2–4 game jams:** finish something playable within days; practise scoping and shipping.
3. **Ship a tiny game (1–3 months):** publish free or cheaply on itch.io to learn the full pipeline end to end.
4. **Pick your first commercial project:** a small, marketable hook in a healthy genre, with a 6–18-month scope; validate with comps.
5. **Prototype and pass gate 1:** prove the core loop is fun with outside playtesters.
6. **Build the vertical slice:** final art style, first trailer, Steam page live, start collecting wishlists.
7. **Production with milestones:** monthly playable builds, regular devlog and social posts, festivals, a public demo.
8. **Next Fest and launch planning:** join the last Next Fest before launch, set the date, send keys to creators and press.
9. **Launch and support:** patch fast, update, join sales, then port or localise if the game resonates.
10. **Post-mortem and next game:** reuse code, tools and audience; most successful indie studios had earlier, smaller releases.

## 20. Glossary, resources and sources

### 20.1 Glossary

| Term | Meaning |
| --- | --- |
| AAA | Big-budget games from large studios and publishers |
| Alpha / Beta | Feature-complete build / content-complete build in polish and bug fixing |
| Asset flip | A game assembled mostly from purchased assets with little original work |
| Capsule | Steam's store artwork shown in lists and search results |
| Comps | Comparable titles used to estimate market potential |
| Core loop | The main repeated cycle of player actions and rewards |
| Delta time | Time elapsed since the previous frame, used to keep movement frame-rate independent |
| ECS | Entity Component System, a data-oriented architecture pattern |
| GDD | Game design document |
| Gold master / RC | Final release build / release candidate |
| Greybox | Untextured placeholder geometry used to test layout and mechanics |
| Juice | Feedback effects (screen shake, particles, sound) that make actions feel good |
| LOD | Level of detail: simpler versions of models at a distance |
| Next Fest | Steam's thrice-yearly demo festival |
| Recoup | A publisher recovering its advance and costs from revenue before splitting |
| TRC / XR / Lotcheck | Certification requirements of Sony, Microsoft and Nintendo |
| Vertical slice | A short section of the game at final quality |
| Wishlist | A Steam player's saved interest; notified at launch and discounts |

### 20.2 Recommended resources

- **Books:** The Art of Game Design (Jesse Schell), Game Programming Patterns (Robert Nystrom, free online), Blood, Sweat, and Pixels (Jason Schreier), A Theory of Fun (Raph Koster), Game Feel (Steve Swink).
- **Websites and newsletters:** How To Market A Game, GameDiscoverCo, GameDev Reports, Game Developer (gamedeveloper.com), GDC Vault talks (many free on YouTube).
- **YouTube:** GMTK (Game Maker's Toolkit), Brackeys, GDC, Sebastian Lague, Thomas Brush, Juniper Dev devlogs.
- **Engine documentation:** Unity Learn, Godot Docs, Unreal Learning (Epic Developer Community).
- **Communities:** r/gamedev, r/IndieDev, engine Discords, local meetups; in the Netherlands, Dutch Game Garden and the Dutch Games Association.
- **Accessibility:** Game Accessibility Guidelines.

### 20.3 Sources

- KitGuru: Steam data shows over 19,000 games released in 2025 — https://www.kitguru.net/gaming/joao-silva/steam-data-shows-over-19000-games-released-in-2025/
- Game World Observer: indie projects generated a quarter of Steam revenue in 2025 — https://gameworldobserver.com/2025/12/22/indie-projects-generated-a-quarter-of-the-total-game-revenue-on-steam-by-the-end-of-2025-analytics
- Notebookcheck: indie games accounted for 25% of Steam's revenue in 2025 — https://www.notebookcheck.net/Indie-games-accounted-for-25-of-Steam-s-revenue-in-2025.1189429.0.html
- VoxBooster: indie game statistics 2026 — https://voxbooster.com/blog/indie-game-statistics-2026
- MP1st: half of 2025 Steam releases have fewer than 10 reviews — https://mp1st.com/news/18k-games-released-steam-2025-half-have-10-reviews
- Yahoo Tech: thousands of 2025 Steam games did not recover the $100 fee — https://tech.yahoo.com/gaming/articles/over-5-000-games-released-152604830.html
- GameDev Reports: Video Game Insights game engines on Steam — https://gamedevreports.substack.com/p/video-game-insights-game-engines
- Game Industry Library: The Big Game Engine Report 2025 — https://gameindustrylibrary.com/writers/video-game-insights
- Unity: changes to subscription plans and pricing — https://unity.com/products/pricing-updates
- Unreal Engine licensing — https://www.unrealengine.com/en-US/license
- Godot maintenance releases (forum) — https://forum.godotengine.org/tag/maintenance-release/55
- Notebookcheck: Steam updates AI disclosure form (January 2026) — https://www.notebookcheck.net/Steam-updates-AI-disclosure-form-requiring-developers-to-report-visible-and-in-game-AI-but-not-background-tools.1206103.0.html
- Outlook Respawn: Valve clarifies Steam AI policy — https://respawn.outlookindia.com/amp/story/gaming/gaming-news/valve-clarifies-steam-ai-policy-focus-shifts-to-content-consumed
- Fragwyz: three years of AI on Steam — https://fragwyz.substack.com/p/three-years-of-ai-on-steam
- Promise Legal: AI game assets in 2026 — https://blog.promise.legal/ai-game-assets-copyright-steam-disclosure-2026/
- Kronis summary of Kellen Voyer's publishing deal analysis — https://links.kronis.dev/q5gvf
- GameDev Reports: Voyer Law publishing agreements in 2025 — https://gamedevreports.substack.com/p/weekly-gaming-reports-recap-may-12
- Bugnet: how indie game publisher deals work — https://bugnet.io/blog/how-indie-game-publisher-deals-work
- Creative Industries Fund NL — https://www.stimuleringsfonds.nl/en/info
- Dutch Games Industry: funds overview — https://www.dutchgamesindustry.nl/funds
- Cinevva: Steam Next Fest strategy 2026 — https://app.cinevva.com/guides/steam-next-fest-strategy.html
- Steam Page Analyzer: after Steam Next Fest — https://www.steampageanalyzer.com/blog/after-steam-next-fest

Original living document: https://claude.ai/code/artifact/5296e96b-2d3d-4a0f-8dd1-33804236e074
