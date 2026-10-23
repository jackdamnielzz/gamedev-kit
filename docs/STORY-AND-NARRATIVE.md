# Story and Narrative Design

> **Master copy:** the GitHub repo `jackdamnielzz/gamedev-kit`, folder `docs/`. Copies elsewhere follow the repo; change the repo first.

23 October 2026 · Niels. Distilled from a deep-research round on what separates games with good stories from games with weak ones, with a focus on strong stories that do not overload the player with text. The key sources are listed at the end of this file.

## Summary

Good game stories live in what the player **does**, not in what the player reads. The tension sits inside the core mechanic, characters react to facts the player created, and the player's own inference fills the gaps. Weak stories show the opposite pattern: a plot that contradicts the mechanics, exposition in unskippable blocks, lines that repeat, and a story that dries up while the loop keeps grinding.

For a game built with this kit (TypeScript, deterministic sim, content as zod-validated JSON, a solo developer with Claude Code), the practical recipe is:

1. Make the core trade-off of the game the story's engine; write it down in one sentence.
2. Deliver everything else as tiny, state-keyed fragments: one-line barks, a recap (newspaper, radio, a notice board), sprite changes in the world.
3. Drive them with a deterministic **storylet engine**, a weekly or daily **pacing director**, layered **anti-repetition** rules and an append-only **chronicle**, so simulation outcomes read as authored history.
4. Plan content for the **whole run**: the most common failure is not too much text but a mid-game drought.

Evidence quality: mostly practitioner talks, developer interviews and critic reviews, not controlled studies. There is no public data on how many players skip dialogue. Numbers below marked "starting value" are design recommendations to tune in playtests.

## Principles

### Story in the verbs

- **Ludonarrative harmony.** When the gameplay's promise ("seek power and you will progress") contradicts the story's promise ("help Atlas and you will progress"), the game "seems to openly mock the player" (Clint Hocking on BioShock). If the fiction says "on the edge", the numbers must be tight.
- **Mechanic first, fiction second.** Papers, Please (Lucas Pope), Undertale (Toby Fox: the story came "after [the] battle system") and Reigns (four bars, binary choices) built the loop before the story. The moral tension lives inside the loop: feed your family versus admit only valid papers.
- **Name the trade-off.** Every game gets one sentence naming the trade-off the player must feel. Every system should make it hurt, not explain it.

### The player writes the rest

- **Apophenia.** Players see "personality and intent where there is none"; the simulation "does the logistics and generates some random outcomes, while the player adds the meaning" (Tynan Sylvester, RimWorld). Show the behaviour (who is drinking at the bar, whose seat is empty), do not narrate it. "Choose the minimum representation that supports the kinds of stories you want to generate."
- **Environmental storytelling.** Subtext that turns simple scenes into "what happened here" (Harvey Smith and Matthias Worch). Answer "where am I?" within 15 seconds; never break the world's rules once set; stage cause and effect with clues instead of words (Don Carson).
- **Evoked narrative.** Spaces that lean on stories players already know (Henry Jenkins) cost nothing: a genre, an era or a place the audience recognises.
- **Ambiguity and no verdicts.** This War of Mine refuses to moralise; remorse is "raised from inside". Name who was hurt by a decision; never tell the player what to feel about it.

### Writing in few words

- **Short, never repeated, specific.** "The lines have to be short"; "nothing sucks the momentum out of the game's narrative like a repeated line"; say "something the player could not have known" (Greg Kasavin, Bastion). Supergiant cut hundreds of lines that did not improve play.
- **Friction makes character.** Characters "refuse to answer questions, leave before you've exhausted everything they might say" (Jon Ingold, inkle). No exhaustible dialogue trees.
- **Every character has a job.** "Every character needs to contribute to the mechanics", plus a visual and vocal hook (Chris Avellone). NPCs as "stars" with visible passions that react to the player (Ken Levine, "narrative Legos").
- **Character template:** one want, one flaw, one visual tic, one catchphrase, one mechanical role, one visible passion.
- **Tone.** One consistent voice lets sparse lines hang together. "Mild peril" is "the most entertaining kind" (Ingold). Write a one-page **voice guide** (register, banned words, sample lines) and give it to Claude Code with every content task.

### Choice and reactivity

- Players do not, on average, dislike the illusion of choice, and dilemmas work without long-term branching. Prefer choices that set tone or relationships (Kentucky Route Zero) over plot branches that multiply content.
- **Reactivity beats volume.** Hades characters comment on the last run, once per moment, so they never run dry; they notice the player's progress "like a haircut". Callbacks weeks later answer Ingold's "show me why I did that".

## Lessons from games

| Game | What it does with little text | Transferable lesson |
| --- | --- | --- |
| Papers, Please | Core loop + daily newspaper + family budget | A recurring recap (newspaper, radio) and a budget screen as moral pressure |
| This War of Mine | No moral verdict, consequences shown in people | Show who was hurt; never moralise |
| Frostpunk | Hope and discontent meters; grey dilemmas | Abstract meters can carry emotion |
| Into the Breach | One- or two-line pilot barks; traits double as backstory | Traits that are also lore; barks after events |
| Hades | Reactive lines, once per moment | Townsfolk react to the last cycle, with seen-once flags |
| Citizen Sleeper | Dice and progress clocks bind multi-day plots | A visible clock per plot thread |
| Night in the Woods | Walkable small town, one hangout per day, short bubbles | A small, recurring, strongly voiced cast in a walkable place |
| Kentucky Route Zero | Choices set tone and memory, not plot | Tone choices cost no downstream content |
| Disco Elysium | About 1M words, made bearable by small nodes and arguing inner voices | Borrow the small-node feed, not the volume |
| Journey, Inside | Wordless; music and environment carry everything | The principle, not the budget |
| **Punch Club (warning)** | After the halfway point "a single continuous grind"; the town map becomes "basically abandoned"; fights are passive | Spread story across the whole run; keep every location useful to the end; give the player a decision during the spectacle |

## Narrative systems for sims and management games

### Storylets, not branching trees

A **storylet** is "simple, atomic, robust, and recombinable": content + prerequisites + effects (Emily Short). Variants:

- **Quality-based narrative** (Failbetter): storylets gated on numeric qualities.
- **Salience-based**: pick the best-fitting item from a large pool, most specific match first, general fallbacks behind it (Valve's dynamic dialogue matched "hundreds of facts" against "thousands of lines").
- **Casting** (Wildermyth): an event lists roles ("a leader, a hothead") and fills them from the current cast. Too tight and events never fire; too loose and roles blur.
- **Binding** (Kreminski): the storylet fills in the actual entities that met its precondition: "$jealous resents $star".

Build a small home-grown engine instead of making ink or Yarn the backbone. CK3 shows a data-driven event table carries a large strategy game (triggers, weighted options, on_action hooks, cooldowns, delayed chains, an explicit weighted "no event"). Use inkjs at most inside a storylet for a rare long scene, and never let it own game state. Copy Yarn Spinner's default saliency strategy: filter failing conditions, prefer the most specific match, penalise recently seen content.

Suggested schema (design proposal, adapt per game):

```ts
Storylet = {
  id, pool,                                   // e.g. a location, "recap", "bark"
  tier: "critical" | "story" | "flavor" | "bark",
  cast: Role[], when: Cond[],                 // conditions are plain data, not code
  weight, cooldown, tagCooldowns?, once?,
  beats: Beat[], choices?: Choice[], effects: Effect[]
}
// selector: pure (state, storylets, seededRng) => Selection; the sim reducer applies effects
```

- Selection order: filter → cast → score by tier, then specificity, then recency-weighted weight.
- Trigger pools from **sim hooks** (`onDayEnd`, `onEventResult`, `onThresholdCrossed`, `onLocationEnter`), not a global random pulse, so every beat traces back to something the player did.
- Apply a storylet's effects **before** its text plays: skipping can then never desync the state.

### Pacing across a calendar

- **A director.** RimWorld's storytellers weigh colony state and "time since the last major event"; Cassandra "pushes you with dangerous events, then gives breathing room". Have a `director.plan()` per day or week compute tension from the game's stress values, set the content budget, and keep an explicit "no event" weight so quiet periods happen on purpose.
- **Failbetter structures** for repeating calendars:
  - **Carousel:** a timing quality unlocks storylets as it climbs, then resets (the build-up to a recurring event).
  - **Grandfather Clock:** a fast "minute hand" quality whose threshold advances a slow main chain (heat → stage).
  - **Midnight Buffet:** a payoff that needs several qualities at once.
- **Text budget per cycle (starting value):** at most 1 scene with a choice, 2–3 one-line barks, 1 recap; at most 1 critical beat; everything else shown in the world (sprites, posters, crowds, mail).
- **Second-half content.** Plan new threats, places and event types for the second half of the run; Punch Club 2 drew the same complaint as Punch Club about a repetitive second half and a weak ending.

### Anti-repetition, in layers

Pool size alone fails: Monster Prom's 388 events still repeat in long play. Stack:

- `once` flags for key beats;
- per-storylet and per-tag cooldowns;
- a least-recently-seen penalty;
- a per-character spotlight cooldown;
- 3–5 variants for frequent barks;
- inline personality variants, so one event fits whoever is cast.

Greg Kasavin warned that Hades' event system became hard to manage without a view of how events connect. Build a **debug overlay** of the current candidate storylets and their scores before content passes about 50 storylets, and a **`lint:story`** step: zod parse, length caps, and a reachability simulation over 1,000 seeded runs that flags storylets firing in under 1% of runs and any cooldown violations.

### The chronicle

Dwarf Fortress (Legends mode) and Wildermyth (Legacy) make generated history feel authored by recording it. Let the **sim** write an append-only `chronicle` of significant events; the narrative layer only reads it. Generate from it:

- a recurring recap (newspaper, radio show, notice board) from the top-scored entries through templated grammars;
- history pages for characters;
- callback conditions for storylets ("after what happened in March").

## Text and UX rules

- **Everything skippable.** A tap completes the typewriter effect, a hold fast-skips; 76.7% of 662 ResetEra voters wanted skipping allowed.
- **At most about three boxes before the player acts** (an old Bethesda rule of thumb).
- **Put text at the decision point.** Eye-tracking (64 players) shows players read task-relevant text and skip ambient text.
- **Short lines:** barks of 12 words or fewer, beats capped at about 280 characters (starting values), enforced in `lint:story`.
- **Speaker portrait + per-character text blip pitch** (Undertale style) instead of voice acting; a visual speaker indicator; highlighted keywords.
- **Dialogue log**, a "story so far" line and the current goal in the menu.
- **Readable pixel font** at a large default size in a solid high-contrast box; an optional clean or large font.
- **Hook in the first 1–3 scenes:** a concrete, personal conflict.
- **Introduce characters one or two at a time**, through play, never as a roster dump.
- **No glossary screens:** teach terms through visible reactions in the world.
- Audience: Quantic Foundry places Story in the Immersion motivation cluster; many players of systems-driven games tolerate story rather than seek it. In a management or sim game, story is seasoning on the systems, never a gate in front of them.

## Checklist for a new game

| # | Do this |
| --- | --- |
| 1 | Write the core trade-off in one sentence; check every system makes it felt |
| 2 | Tune the economy so the fiction's stakes are true in the numbers |
| 3 | Write a one-page voice guide and attach it to every content task |
| 4 | Give every character a want, flaw, visual tic, catchphrase, mechanical role and visible passion |
| 5 | Every line references a fact the player created; no generic filler without a specific variant above it |
| 6 | Characters withhold, refuse and leave; no exhaustible dialogue trees |
| 7 | Per location, define 3–5 state-driven sprite swaps |
| 8 | Keep every location mechanically useful until the end |
| 9 | Storylets as zod-validated JSON with `when`, `cast`, `tier`, `weight`, cooldowns, `once`, `beats`, `choices`, `effects` |
| 10 | Pure, seeded selector; trigger from sim hooks; apply effects before text |
| 11 | A pacing director with push/rest cycles and an explicit "no event" weight |
| 12 | Carousel / Grandfather Clock / Buffet for recurring events, progress and payoffs |
| 13 | A text budget per cycle (start: 1 scene, 2–3 barks, 1 recap) |
| 14 | Plan fresh content for the second half of the run |
| 15 | Layered anti-repetition; 1,000-run seeded simulation in `lint:story` |
| 16 | Debug overlay of candidate storylets and scores before content passes ~50 storylets |
| 17 | Sim writes an append-only chronicle; recap, history pages and callbacks read it |
| 18 | Text UX: skippable, ≤ 3 boxes before acting, text at decision points, portraits and blips, log, readable font |
| 19 | A personal hook in the first 1–3 scenes |
| 20 | Leave out what turns the game into a spreadsheet or a text wall; teach through reactions in the world |

## Key sources

- Clint Hocking, ludonarrative dissonance: https://www.clicknothing.com/click_nothing/2007/10/ludonarrative-d.html
- Designing Papers, Please: https://www.gamedeveloper.com/design/designing-the-bleak-genius-of-i-papers-please-i-
- Tynan Sylvester on apophenia: https://gdt.stanford.edu/how-do-you-create-apophenia/
- Harvey Smith on environmental storytelling: https://niemanstoryboard.org/2011/01/14/harvey-smith-on-environmental-storytelling-and-embedding-narrative/
- Don Carson, environmental storytelling: https://www.gamedeveloper.com/design/environmental-storytelling-creating-immersive-3d-worlds-using-lessons-learned-from-the-theme-park-industry
- Henry Jenkins, Game Design as Narrative Architecture: https://web.mit.edu/~21fms/People/henry3/games&narrative.html
- Greg Kasavin, writing Bastion: https://www.supergiantgames.com/blog/in-depth-writing-bastion/
- Jon Ingold interview: https://punishedbacklog.com/interview-jon-ingold-inkle-studios/
- Jon Ingold, designing 80 Days: https://www.gamedeveloper.com/design/threats-luggage-and-mild-peril-designing-i-80-days-i-
- Chris Avellone on memorable characters: https://gameranx.com/updates/id/9558/article/project-eternity-chris-avellone-discusses-how-to-build-memorable-characters/
- Ken Levine, narrative Legos: https://gameinformer.com/b/news/archive/2014/03/22/ken-levine-talks-player-participation-and-breaking-away-from-linear-narratives
- Emily Short, storylets: https://emshort.blog/2019/11/29/storylets-you-want-them/ · Beyond Branching: https://emshort.blog/2016/04/12/beyond-branching-quality-based-and-salience-based-narrative-structures/ · Kreminski: https://emshort.blog/2019/01/06/kreminski-on-storylets/
- Failbetter, narrative structures: https://www.failbettergames.com/news/new-narrative-structures
- Elan Ruskin, AI-driven dynamic dialog (GDC): https://www.gdcvault.com/play/1015528/AI-driven-Dynamic-Dialog-through
- Yarn Spinner, storylets and saliency: https://docs.yarnspinner.dev/write-yarn-scripts/advanced-scripting/storylets-and-saliency-a-primer
- CK3 event modding: https://ck3.paradoxwikis.com/Event_modding
- RimWorld AI storytellers: https://rimworldwiki.com/wiki/AI_storytellers
- Wildermyth interview: https://turnbasedlovers.com/10-turns-interview/with-wildermyth-developer
- Hades narrative (Kasavin): https://www.gameshub.com/news/features/hades-greg-kasavin-breaks-down-supergiants-unique-approach-to-narrative-262459-2193/
- Punch Club review (grind, abandoned town): https://techraptor.net/content/punch-club-review-aint-gonna-be-no-rematch
- Why players skip: https://fredzed.substack.com/p/why-do-players-skip
- Eye-tracking study of subtitles in games: https://pmc.ncbi.nlm.nih.gov/articles/PMC12452717/
- ResetEra poll on skippable cutscenes: https://www.resetera.com/threads/its-2023-can-a-new-years-resolution-for-every-dev-be-no-unskippable-cut-scenes.688750/
- Game Accessibility Guidelines: https://gameaccessibilityguidelines.com/full-list/
- Quantic Foundry, gamer motivation map: https://quanticfoundry.com/2015/12/21/map-of-gaming-motivations/
