#!/usr/bin/env node
// gamedev-kit SessionStart hook: tells every session in a game folder to read the kit's
// documentation before it starts working. Runs only where the plugin is enabled (project scope).
// Output: JSON with additionalContext (kept well under the 10,000-character hook limit).
'use strict';
const fs = require('fs');
const path = require('path');

let input = {};
try { input = JSON.parse(fs.readFileSync(0, 'utf8') || '{}'); } catch { /* no stdin */ }

const root = (process.env.CLAUDE_PLUGIN_ROOT || path.resolve(__dirname, '..')).replace(/\\/g, '/');
const project = process.env.CLAUDE_PROJECT_DIR || input.cwd || process.cwd();
const source = input.source || 'startup';
const docs = (f) => `${root}/docs/${f}`;
const isExisting = fs.existsSync(path.join(project, 'docs', 'specs', '000-stack.md'));

const lines = [];
lines.push('GAMEDEV-KIT BRIEFING (from the gamedev-kit plugin, enabled for this game folder).');

if (source === 'compact' || source === 'resume') {
  lines.push(
    'This session was ' + (source === 'compact' ? 'compacted' : 'resumed') + '. The rules in ' + docs('START-HERE.md') +
      ' still apply: English for everything, reference-first art, the animation decision guide, real pixel art cleanup (scripts + Sprite Grid), cost checks, the asset manifest, and a model recommendation per task.',
    'If you no longer have the relevant kit sections in context, re-read them before continuing the current task.'
  );
} else if (!isExisting) {
  lines.push(
    'This folder has no docs/specs/000-stack.md yet, so treat it as a NEW GAME.',
    'Before you write code, propose a stack, draft a concept or generate any asset, READ THESE IN FULL, in order (use the Read tool; do not rely on memory):',
    '  1. ' + docs('START-HERE.md'),
    '  2. ' + docs('GAME-STACK.md'),
    '  3. ' + docs('AI-ASSET-WORKFLOW.md'),
    '  4. ' + docs('indie-game-development-guide.md'),
    '  5. ' + docs('STORY-AND-NARRATIVE.md'),
    '  6. ' + docs('NANOGPT-API.md') + ' (overview now, the rest before the first generation call)',
    'Then give the human a short brief (max 10 lines): the rules you will follow, open questions, and the Claude model you recommend for the next step. Then continue with /gamedev-kit:new-game.',
    'Do this even if the human\'s first message asks you to start building right away; tell them you are reading the kit first.'
  );
} else {
  lines.push(
    'This is an EXISTING GAME (docs/specs/000-stack.md exists). Before your first task in this session:',
    '  - read ' + docs('START-HERE.md') + ' (the standing rules);',
    '  - read the project CLAUDE.md, docs/concept.md and every file in docs/specs/ (project decisions win over the kit);',
    '  - for the task at hand, read the matching kit sections: art/animation -> ' + docs('AI-ASSET-WORKFLOW.md') +
      '; architecture/testing/tooling -> ' + docs('GAME-STACK.md') + '; scope/release/marketing -> ' + docs('indie-game-development-guide.md') +
      '; story/dialogue/events -> ' + docs('STORY-AND-NARRATIVE.md') + '.',
    'Re-read the full documents before a new asset group, a new major system or a stack change.'
  );
}
lines.push('Everything in this project is in English: replies, code, docs, in-game text and all prompts for AI tools.');

process.stdout.write(JSON.stringify({
  hookSpecificOutput: { hookEventName: 'SessionStart', additionalContext: lines.join('\n') },
}));
