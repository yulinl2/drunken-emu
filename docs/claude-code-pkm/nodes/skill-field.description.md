---
id: skill-field.description
kind: skill-field
status: VERIFIED
title: "description"
sources: [S32]
---

# description

**Sources:** [S32](src.s32.md)

What the skill does and when to use it. Claude uses this to decide when to apply the skill. If omitted, uses the first non-empty line of the markdown content. Put the key use case first: the combined `description` and `when_to_use` text is truncated at 1,536 characters in the skill listing to reduce context usage. (required: Recommended)
