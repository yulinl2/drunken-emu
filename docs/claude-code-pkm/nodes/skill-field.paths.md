---
id: skill-field.paths
kind: skill-field
status: VERIFIED
title: "paths"
sources: [S32]
---

# paths

**Sources:** [S32](src.s32.md)

Glob patterns that limit when this skill is activated. Accepts a comma-separated string or a YAML list. When set, Claude loads the skill automatically only when working with files matching the patterns. Patterns are relative to Claude's current working directory, and files outside that directory don't match. Uses the same glob format as path-specific rules. (required: No)
