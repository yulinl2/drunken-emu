---
id: feature.pre-approve-tools-for-a-skill
kind: feature
status: VERIFIED
title: "Pre-approve tools for a skill"
sources: [S32]
---

# Pre-approve tools for a skill

**Sources:** [S32](src.s32.md)

The `allowed-tools` field grants permission for the listed tools during the turn that invokes the skill, so Claude can use them without prompting you for approval. The grant clears when you send your next message, even though the skill content stays in context; invoking the skill again re-applies it for that turn. It does not restrict which tools are available: every tool remains callable, and you
