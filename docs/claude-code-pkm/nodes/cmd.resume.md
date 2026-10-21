---
id: cmd.resume
kind: command
status: VERIFIED
title: "/resume"
sources: [S80]
---

# /resume

**Sources:** [S80](src.s80.md)

Resume a conversation by ID or name, or open the session picker. Background sessions appear in the picker marked with `bg`. Resuming one that is still running, from the picker or by ID or name, opens that session: your current conversation moves to the background and this terminal attaches to the running one. Press `←` on an empty prompt to return to agent view, which also lists the conversation you left. Before v2.1.285, Claude Code refused and told you to open the session with `claude attach` or stop it first. Alias: `/continue`
