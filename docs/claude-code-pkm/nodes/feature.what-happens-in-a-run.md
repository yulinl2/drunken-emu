---
id: feature.what-happens-in-a-run
kind: feature
status: VERIFIED
title: "What happens in a run"
sources: [S47]
---

# What happens in a run

**Sources:** [S47](src.s47.md)

For each run of a case, Claude Code starts a fresh, isolated non-interactive session with only your plugin loaded, sends the prompt, and lets Claude work until it finishes or hits the case's turn or time limit. Each grader then checks the final reply, the transcript, or a file Claude created, and passes or fails.
