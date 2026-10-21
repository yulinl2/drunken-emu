---
id: skill-field.disable-model-invocation
kind: skill-field
status: VERIFIED
title: "disable-model-invocation"
sources: [S32]
---

# disable-model-invocation

**Sources:** [S32](src.s32.md)

Set to `true` to prevent Claude from automatically loading this skill. Use for workflows you want to trigger manually with `/name`. Also prevents the skill from being preloaded into subagents and from running when a session-scoped scheduled task fires with the skill as its prompt. Default: `false`. (required: No)
