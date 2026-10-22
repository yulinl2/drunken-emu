---
id: feature.how-backgrounding-works
kind: feature
status: VERIFIED
title: "How backgrounding works"
sources: [S83]
---

# How backgrounding works

**Sources:** [S83](src.s83.md)

When Claude Code runs a command in the background, it runs the command asynchronously and immediately returns a background task ID. Claude Code can respond to new prompts while the command continues executing in the background.
