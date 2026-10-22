---
id: skill-field.metadata
kind: skill-field
status: VERIFIED
title: "metadata"
sources: [S32]
---

# metadata

**Sources:** [S32](src.s32.md)

Free-form YAML map for your own key-value data, such as entitlement or catalog fields, read by your own tooling from `SKILL.md`. Claude Code doesn't act on its contents, and drops a value that isn't a map. Don't reuse frontmatter field names such as `paths` as keys. (required: No)
