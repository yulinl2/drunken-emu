---
id: feature.concurrent-subagent-limit
kind: feature
status: VERIFIED
title: "Concurrent subagent limit"
sources: [S25]
---

# Concurrent subagent limit

**Sources:** [S25](src.s25.md)

Two limits control subagent use, each with its own variable: this one stops Claude from spawning more subagents while too many are running, and the depth limit caps how deeply subagents nest. There's no limit on the total number of subagents Claude can spawn over a session.
