---
id: feature.recall-a-prompt-that-had-pasted-text
kind: feature
status: VERIFIED
title: "Recall a prompt that had pasted text"
sources: [S74]
---

# Recall a prompt that had pasted text

**Sources:** [S74](src.s74.md)

Claude Code keeps the content behind each `[Pasted text #N]` placeholder under `~/.claude/paste-cache/`, so when you recall a prompt from command history and resubmit it, the full pasted content is sent again, including in a later session.
