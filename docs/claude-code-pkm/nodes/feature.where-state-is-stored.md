---
id: feature.where-state-is-stored
kind: feature
status: VERIFIED
title: "Where state is stored"
sources: [S26]
---

# Where state is stored

**Sources:** [S26](src.s26.md)

Session state is stored under your Claude Code config directory. If you set `CLAUDE_CONFIG_DIR`, the supervisor uses that directory instead of `~/.claude` and runs as a separate instance with its own sessions.
