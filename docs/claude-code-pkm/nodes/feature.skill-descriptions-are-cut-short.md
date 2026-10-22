---
id: feature.skill-descriptions-are-cut-short
kind: feature
status: VERIFIED
title: "Skill descriptions are cut short"
sources: [S32]
---

# Skill descriptions are cut short

**Sources:** [S32](src.s32.md)

Claude Code loads a listing of skill names and descriptions into context so Claude knows what's available. The listing always contains every skill name, but if you have many skills, Claude Code drops some descriptions to fit the listing's character budget, which removes the keywords Claude needs to match your request. The budget scales at 1% of the model's context window. When the listing overflow
