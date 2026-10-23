---
name: story-design
description: Story and narrative design without text overload - principles (story in the verbs, apophenia, environmental storytelling, short never-repeating reactive lines, character templates, voice guide), lessons from story-light games, a deterministic storylet engine as zod-validated JSON, pacing directors and calendar structures, layered anti-repetition, the chronicle and recaps, text and dialogue UX, and a checklist. Use when designing a game's story, characters, dialogue, barks, events or narrative systems.
when_to_use: Any question or task about story, plot, characters, dialogue, barks, events, quests, recaps, narrative pacing or narrative tooling in one of Niels's games.
---

# Story design

The full guide lives in `${CLAUDE_PLUGIN_ROOT}/docs/STORY-AND-NARRATIVE.md`. Read the relevant sections with the Read tool before designing or writing story content; do not rely on memory of it.

Section map:

- Summary
- Principles (story in the verbs · the player writes the rest · writing in few words · choice and reactivity)
- Lessons from games (table, including Punch Club as the warning case)
- Narrative systems for sims and management games (storylets · pacing across a calendar · anti-repetition · the chronicle)
- Text and UX rules
- Checklist for a new game
- Key sources

Rules when using it:

- The project's own `docs/concept.md`, specs and voice guide win over the kit.
- Write every line in English and in the project's voice guide; if the project has no voice guide yet, propose one first.
- Story content is data (storylets in JSON validated by zod); the sim applies effects, the narrative layer only reads state and the chronicle.
- Budgets and thresholds in the guide are starting values; tune them in playtests.
- Recommended model: Opus for story structure, characters and the voice guide; Sonnet for writing storylet data against an approved structure.
