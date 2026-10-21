---
id: feature.run-skills-in-a-subagent
kind: feature
status: VERIFIED
title: "Run skills in a subagent"
sources: [S32]
---

# Run skills in a subagent

**Sources:** [S32](src.s32.md)

Add `context: fork` to your frontmatter when you want a skill to run in isolation. Claude Code starts a new subagent of the type set in the `agent` field and gives it the skill content as its prompt. The subagent doesn't see your conversation history, so the skill's instructions have to stand on their own.
