---
id: feature.start-faster-with-bare-mode
kind: feature
status: VERIFIED
title: "Start faster with bare mode"
sources: [S38]
---

# Start faster with bare mode

**Sources:** [S38](src.s38.md)

Add `--bare` to reduce startup time by skipping auto-discovery of hooks, skills, custom commands, subagents, installed plugins, MCP servers, auto memory, and CLAUDE.md. Without it, `claude -p` discovers and loads them as an interactive session would, including anything configured in the working directory or `~/.claude`.
