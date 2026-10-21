---
id: feature.what-the-saved-script-looks-like
kind: feature
status: VERIFIED
title: "What the saved script looks like"
sources: [S29]
---

# What the saved script looks like

**Sources:** [S29](src.s29.md)

When you save a workflow, the file in `.claude/workflows/` holds a `meta` block followed by a script body that orchestrates subagents. You usually don't need to edit it, but here is the shape of a small one so you can recognize what Claude generated:
