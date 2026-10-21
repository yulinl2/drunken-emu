---
id: feature.use-ultrathink-for-one-off-deep-reasoning
kind: feature
status: VERIFIED
title: "Use ultrathink for one-off deep reasoning"
sources: [S70]
---

# Use ultrathink for one-off deep reasoning

**Sources:** [S70](src.s70.md)

Include `ultrathink` anywhere in your prompt to request deeper reasoning on that turn without changing your session effort setting. Claude Code recognizes the keyword and adds an in-context instruction. The effort level sent to the API is unchanged. Claude Code passes other phrases such as "think", "think hard", and "think more" through as ordinary prompt text and doesn't recognize them as keyword
