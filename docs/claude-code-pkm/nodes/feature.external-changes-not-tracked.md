---
id: feature.external-changes-not-tracked
kind: feature
status: VERIFIED
title: "External changes not tracked"
sources: [S84]
---

# External changes not tracked

**Sources:** [S84](src.s84.md)

Checkpointing only tracks files that have been edited within the current session. Manual changes you make to files outside of Claude Code and edits from other concurrent sessions are normally not captured, unless they happen to modify the same files as the current session.
