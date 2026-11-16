# Game feel — responsiveness, feedback and forgiveness

> **Master copy:** the GitHub repo `jackdamnielzz/gamedev-kit`, folder `docs/`. Copies elsewhere follow the repo; change the repo first.

16 November 2026 · Niels. Game feel decides whether the core verb is fun before any art exists, and it is the one thing an agent cannot judge by itself: it cannot hold a controller. This page gives concrete starting values, says where each one lives in the kit's architecture, and turns "does it feel good?" into checks an agent can run and a tuning loop the human controls.

Evidence: practitioner talks and books (listed at the end), not controlled studies. **Every number on this page is a starting value** to tune in play, not a rule.

## Summary

Game feel has three parts:

1. **Response**: the game reacts to input at once and predictably.
2. **Feedback**: every action and every hit is confirmed by picture and sound, in proportion to how much it matters.
3. **Forgiveness**: the game reads what the player meant, not only what the frame-exact input said (buffering, coyote time, corner correction).

The kit's rules for feel:

- **Response first, juice second.** Effects cannot rescue a sluggish verb; they hide the problem until playtests. Fix latency and control curves before adding shake and particles.
- **Feel is data.** Every value lives in `data/feel.json` (validated like other content), never as a magic number in code.
- **Timing that changes outcomes lives in the sim, in ticks.** Pure presentation lives in the render and audio layers.
- **The agent checks; the human tunes.** Claude writes tick tests and reads filmstrips; the human tunes values live in a tuning panel; tuned values go back into `data/feel.json` with a dated decision.
- **Feel gets a gate.** The core verb must feel good with greybox art at gate 1 of the indie guide, before the vertical slice.

## 1. Where feel lives in the architecture

| What | Layer | Unit | Why |
| --- | --- | --- | --- |
| Input buffer, coyote time, corner correction, acceleration and friction, jump arcs, cancel windows, gameplay hit-stop (attack paused on impact) | `src/sim` (Godot: `sim/`) | Ticks | Changes outcomes: must be deterministic, in replays and in tests |
| Screen shake, flashes, squash and stretch, particles, camera smoothing, number tweens, UI easing | `src/render`, `src/ui` | Milliseconds or render frames | Presentation only; never writes sim state |
| Sound variation, ducking, layered impacts | `src/audio` | Milliseconds, semitones, dB | Reacts to sim events |

- **Tick rate.** At 30 ticks per second one tick is 33 ms, too coarse for buffer windows and hit-stop in an action game. Use 60 ticks per second for platformers, fighters and action games; 20–30 is fine for strategy, management and card games.
- **Visual randomness** (shake noise, particle spread) may use its own unseeded generator in the render layer, but give it a fixed seed in test mode so screenshots and filmstrips are stable.
- **One file:** `data/feel.json`, with a zod schema (Godot: a schema check at load) that gives every value a range. Example shape:

```json
{
  "tick_rate": 60,
  "input": { "buffer_ticks": 8, "coyote_ticks": 6 },
  "move": { "accel_ticks_to_max": 5, "stop_ticks": 3, "max_speed_px_s": 140 },
  "jump": { "rise_gravity": 900, "fall_gravity_mult": 2.0, "release_cut": 0.5, "apex_gravity_mult": 0.5, "max_fall_px_s": 320, "corner_correction_px": 3 },
  "hit": { "hitstop_ticks_light": 4, "hitstop_ticks_heavy": 8, "flash_frames": 2, "knockback_px": 4 },
  "camera": { "follow_lerp": 0.15, "lookahead_px": 24, "deadzone_px": [16, 12] },
  "shake": { "trauma_decay_per_s": 1.2, "max_offset_px": 4, "max_angle_deg": 1.5, "noise_hz": 25 },
  "ui": { "enter_ms": 200, "exit_ms": 120, "count_up_ms": 500 }
}
```

## 2. Starting values

### 2.1 Response and control (action games)

| Value | Start at | Notes |
| --- | --- | --- |
| First visible reaction to input | The next rendered frame | Show the anticipation pose or a sound at once, even when the action itself has a wind-up |
| End-to-end input latency | Under about 100 ms for action games | Measure it (section 3); browser and display add latency you do not control |
| Input buffer (jump, attack, dash) | 100–150 ms (6–9 ticks at 60 Hz) | A press slightly before landing or recovery still counts |
| Coyote time | 80–120 ms (5–7 ticks) | A jump just after leaving a ledge still counts |
| Variable jump height | Multiply upward speed by 0.4–0.6 on release | Short taps give short hops |
| Fall gravity | 1.5–2.5× rise gravity, with a maximum fall speed | Removes the floaty "moon jump" |
| Apex hang | About half gravity near the top while jump is held | More control at the peak |
| Corner correction | Nudge 2–4 px at a 320–640 px base width | Clipping a ceiling corner should not kill a jump |
| Acceleration | Top speed in 3–6 frames (snappy) or 10–20 (heavy) | **Decide the weight first** and write it in the feel spec |
| Stopping and turning | Faster than accelerating | Turning should never feel slower than starting |
| Cancel windows | Let movement or dodge cancel the end of an attack | Long uncancellable recoveries read as unresponsive |

### 2.2 Impact feedback

| Value | Start at | Notes |
| --- | --- | --- |
| Hit-stop | 3–8 frames (50–130 ms) at 60 Hz, longer for heavy hits | Freeze attacker and target; skip it on every tick of a multi-hit; put it in the sim when it delays gameplay |
| Hit flash | Target white or tinted for 1–3 frames | Confirms which target was hit |
| Knockback | 2–6 px plus a short velocity | Direction away from the hit |
| Screen shake | Trauma model: trauma 0–1 added per event, shake = trauma² (or ³), decays about 1–1.5 per second | Smooth noise, not uniform random per frame; a small directional kick along the hit; clamp trauma at 1 so stacked events do not explode |
| Shake size | 2–6 px offset at base resolution, rotation at most 1–3° | Shake the world camera only, never the UI |
| Squash and stretch | 10–25 % on jump and land, back in 80–150 ms | Keep the area roughly the same |
| Particles and debris | 150–500 ms lifetimes, spawned at the contact point | Fewer, bigger particles read better at pixel scale |
| Sound | Every action has a sound; vary pitch ±5–10 % (about ±1 semitone) and volume ±10 % on repeats | Layer impacts: a short transient plus a body |

### 2.3 Camera

- Follow with smoothing (a lerp of 0.1–0.2 per frame at 60 Hz, or critically damped), a small dead zone, and look-ahead in the movement direction.
- Never let the camera hide the next threat or the landing spot; frame what the player must react to.
- Pixel art: round the final camera position to whole pixels after smoothing (or snap 2D transforms in Godot).

### 2.4 UI and menus

| Value | Start at |
| --- | --- |
| Hover and press state | The next frame, always with a sound for presses |
| Panel enter / exit | 150–250 ms ease-out / 100–150 ms ease-in |
| Number count-up (gold, score) | 300–800 ms, with a tick sound |
| Toasts and notifications | Hold 2–3 s; never cover the action |
| Transitions | Interruptible; clicks during a transition are buffered, never lost |

### 2.5 Notes per genre

| Genre | What feel means there |
| --- | --- |
| Platformer | Section 2.1 in full; jump arcs and buffering matter more than any effect |
| Top-down action / ARPG | Attack wind-up shown at once, hit-stop and knockback, dodge with invulnerability frames, cancel windows; click-to-move answers with a marker on the next frame |
| RTS and tactics | Every order is acknowledged at once (click marker, a short unit bark, the unit turns), drag-select follows the mouse without lag, order queues are visible |
| Management and sims | Numbers animate towards their new value, time-speed changes are instant, completions get a small celebration (sound, sparkle, count-up), cause and effect are shown next to each other |
| Card and deck-builders | Cards lift on hover, follow a drag with a slight lag and snap into place; draw, shuffle and play have distinct sounds; resolving effects show their order |
| Puzzle | Undo is instant and unlimited; a move animates in 80–150 ms and input is queued, never blocked |

## 3. How the agent verifies feel

1. **Feel spec.** The core-loop spec (or `docs/specs/NNN-feel.md`) states the intended feeling in words (snappy, heavy, floaty, crunchy), describes two or three reference moments in our own words (never "like <game>" in prompts or shipped text), and lists the parameters that create it.
2. **Tick tests.** Unit tests on the sim prove the rules: a jump pressed `buffer_ticks` before landing fires on the landing tick; a jump pressed `coyote_ticks` after leaving a ledge fires; input on tick *t* changes velocity on tick *t* or *t* + 1; hit-stop lasts exactly the configured ticks; no animation state blocks a buffered input forever. They read the values from `data/feel.json`, so tuning never breaks them.
3. **Filmstrip review.** Record a scripted action (jump, land, hit, menu open) frame by frame and build a filmstrip with frame numbers: Playwright screenshots per frame with the sim stepped by hand on the web, `--write-movie <dir>/frame.png --fixed-fps 60` in Godot, then `art/py/contact_sheet.py`. Claude reads it and checks: a reaction on the first frame after input; hit-stop frames where expected; shake inside the size limits; no pops, teleports or one-frame gaps; effects gone when they should be.
4. **Latency check.** A Playwright test presses a key and counts frames until the first pixel change in the player's area; report the number with every feel change.
5. **Tuning panel.** A dev-only overlay (a key such as F1, or `?tune` in the URL) with a slider for every value in `data/feel.json`, applied live, plus "copy JSON" and "reset". Web: lil-gui (MIT). Godot: a `Control` panel that builds `HSlider`s from the JSON. The human tunes; Claude commits the result to `data/feel.json` and records a dated decision in the spec.
6. **Effects off switch.** A dev key that turns each feedback layer (shake, flash, hit-stop, particles, sound variation) on and off, so the human can compare with and without.
7. **Feel gate.** Before the vertical slice the human plays the core verb for five minutes with greybox art and answers three questions: does the main verb feel good with no art? what feels late, slippery or stiff? which moment felt best? Do not start art or content production until the answer to the first is yes.

## 4. Accessibility

- Settings to turn off or scale screen shake, flashes and camera motion (a single "reduced motion" switch plus an intensity slider); respect the operating system's reduced-motion setting on the web (`prefers-reduced-motion`).
- No more than three flashes per second over a large part of the screen (WCAG 2.3.1, "three flashes or below threshold").
- Remappable controls, hold-or-toggle options, and adjustable buffer and coyote windows in an assist menu cost almost nothing once they are data.

## 5. Pitfalls

| Pitfall | Rule |
| --- | --- |
| Juice added to hide a slow or slippery verb | Measure and fix response first; add feedback after the feel gate |
| Effects pile up into noise when many things happen | Priorities and caps: trauma clamps at 1, at most N simultaneous flashes and sounds per type |
| Hit-stop only in the renderer while the sim keeps running | Gameplay pauses belong in the sim, in ticks |
| A 30 Hz sim in a precise action game | 60 ticks per second |
| Magic numbers spread through the code | Everything in `data/feel.json` with ranges in the schema |
| The agent tunes by its own judgement | The human tunes in the panel; the agent tests and reports |
| Screenshot tests flaky because of random effects | Seed visual randomness in test mode, or turn effects off for snapshot tests |
| Animations that lock input | Cancel windows and input buffering; never drop an input silently |
| Shake applied to the UI layer | Shake the world camera only |

## Sources

- Steve Swink, *Game Feel: A Game Designer's Guide to Virtual Sensation* (2008).
- Martin Jonasson and Petri Purho, "Juice it or lose it" (talk, 2012).
- Jan Willem Nijman (Vlambeer), "The art of screenshake" (talk, 2013).
- Squirrel Eiserloh, "Math for Game Programmers: Juicing Your Cameras With Math" (GDC 2016): trauma-based shake with smooth noise.
- Kyle Pittman, "Math for Game Programmers: Building a Better Jump" (GDC 2016): jump arcs from height and distance.
- Maddy Thorson's notes on the forgiveness mechanics in Celeste (coyote time, jump buffering, corner correction).
- WCAG 2.3.1, Three Flashes or Below Threshold; Game Accessibility Guidelines (gameaccessibilityguidelines.com).
- lil-gui (github.com/georgealways/lil-gui), MIT, for the web tuning panel.
