---
id: feature.resume-a-running-background-session
kind: feature
status: VERIFIED
title: "Resume a running background session"
sources: [S20]
---

# Resume a running background session

**Sources:** [S20](src.s20.md)

When the conversation you resume with `claude --resume` or `/resume` belongs to a background session that is still running, Claude Code opens the running session itself. With `--bg` on the command line, the resume is a background dispatch instead. Before v2.1.285, Claude Code refused and told you to open the session with `claude attach `, or to stop it with `claude stop ` first.
