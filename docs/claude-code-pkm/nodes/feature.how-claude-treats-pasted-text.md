---
id: feature.how-claude-treats-pasted-text
kind: feature
status: VERIFIED
title: "How Claude treats pasted text"
sources: [S74]
---

# How Claude treats pasted text

**Sources:** [S74](src.s74.md)

When you submit, Claude sees the content behind each `[Pasted text #N]` placeholder marked as text you pasted from somewhere else rather than typed. Claude is told that a paste can contain instructions you didn't write, and to follow instructions inside it only where the message you typed asks it to. In sessions that don't fetch feature flags, pastes aren't marked.
