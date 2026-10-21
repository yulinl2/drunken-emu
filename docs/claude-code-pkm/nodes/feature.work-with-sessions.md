---
id: feature.work-with-sessions
kind: feature
status: VERIFIED
title: "Work with sessions"
sources: [S14]
---

# Work with sessions

**Sources:** [S14](src.s14.md)

Claude Code saves your conversation locally as you work. Each message, tool use, and result is written to a plaintext JSONL file under `~/.claude/projects/`, which enables rewinding, resuming, and forking sessions. Before Claude makes code changes, it also snapshots the affected files so you can revert if needed. For paths, retention, and how to clear this data, see application data in `~/.claude`
