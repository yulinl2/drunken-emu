---
id: permission-mode.boundaries-you-state-in-conversation
kind: permission-mode
status: VERIFIED
title: "Boundaries you state in conversation"
sources: [S67]
---

# Boundaries you state in conversation

**Sources:** [S67](src.s67.md)

The classifier treats boundaries you state in the conversation as a block signal. If you tell Claude "don't push" or "wait until I review before deploying", the classifier blocks matching actions even when the default rules would allow them. A boundary stays in force until you lift it in a later message. Claude's own judgment that a condition was met does not lift it.
