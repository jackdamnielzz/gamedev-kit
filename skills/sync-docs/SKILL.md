---
name: sync-docs
description: Keep the gamedev-kit documentation consistent - the GitHub repo jackdamnielzz/gamedev-kit (docs/) is the master; apply doc changes there first, then tell the human how to update the installed plugin and which copies (claude.ai Game Dev project, older game repos) to refresh.
when_to_use: A lesson, decision or tool change should become part of the shared game-dev documentation, or the human runs /gamedev-kit:sync-docs.
disable-model-invocation: true
argument-hint: "[what changed]"
---

# Sync docs

Change: $ARGUMENTS

The master copy of every document is the repo `jackdamnielzz/gamedev-kit`, folder `docs/`. The installed plugin is a read-only copy; edits there are lost on update.

1. Ask the human where their local clone of `gamedev-kit` is (suggest `D:\Programmeren\gamedev-kit`). If there is none, give the clone command: `git clone https://github.com/jackdamnielzz/gamedev-kit.git`.
2. Make the change in that clone: the right document under `docs/`, and, if a workflow changes, the matching `skills/*/SKILL.md` or file under `templates/project/`. Keep docs in English.
3. Show the diff and, after the human agrees, commit with a clear message and push.
4. Tell the human to update the plugin: `claude plugin marketplace update gamedev-kit` then `claude plugin update gamedev-kit@gamedev-kit` (or in a session: `/plugin` → Installed → gamedev-kit → Update now), then start a new session or run `/reload-plugins`.
5. Remind the human that the copies in the claude.ai "Game Dev" project should be replaced with the new versions from `docs/`, and that existing games keep their own `CLAUDE.md` and specs unless they ask to adopt the change.
