---
id: feature.skill-content-lifecycle
kind: feature
status: VERIFIED
title: "Skill content lifecycle"
sources: [S32]
---

# Skill content lifecycle

**Sources:** [S32](src.s32.md)

When you or Claude invoke a skill, the rendered `SKILL.md` content enters the conversation as a single message and stays there across later turns. This persistence applies to the skill's instructions, not its permissions: an `allowed-tools` grant clears when you send your next message. Claude Code does not re-read the skill file on later turns, so write guidance that should apply throughout a task
