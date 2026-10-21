---
id: feature.how-runs-are-isolated
kind: feature
status: VERIFIED
title: "How runs are isolated"
sources: [S47]
---

# How runs are isolated

**Sources:** [S47](src.s47.md)

Each run gets a temporary home directory, working directory, and Claude Code configuration, and the agent under test runs there as a `claude -p` child process with only your plugin loaded. Keep these consequences in mind when you write cases:
