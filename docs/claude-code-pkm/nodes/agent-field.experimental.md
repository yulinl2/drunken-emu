---
id: agent-field.experimental
kind: agent-field
status: VERIFIED
title: "experimental"
sources: [S25]
---

# experimental

**Sources:** [S25](src.s25.md)

Map of experimental options. Set its `cacheTtl` key to `5m` or `1h` to choose the prompt cache lifetime for this subagent's requests, at the frontmatter's place in the cache lifetime precedence. Claude Code ignores any other value, ignores `1h` while your Claude subscription is using usage credits, and reads the field only from subagent files. Requires Claude Code v2.1.248 or later (required: No)
