---
id: plugin.sync-timing-in-terminal-sessions
kind: plugin
status: VERIFIED
title: "Sync timing in terminal sessions"
sources: [S49]
---

# Sync timing in terminal sessions

**Sources:** [S49](src.s49.md)

Because the terminal sync runs in the background, it can finish after your session has started. When it adds, updates, or removes a synced plugin in an interactive session, you see `Plugins changed. Run /reload-plugins to activate.` Run `/reload-plugins` to load the change in that session, or leave it for the next time you start Claude Code.
