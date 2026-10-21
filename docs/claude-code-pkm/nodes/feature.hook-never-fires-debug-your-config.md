---
id: feature.hook-never-fires-debug-your-config
kind: feature
status: VERIFIED
title: "Hook never fires"
sources: [S40]
---

# Hook never fires

**Sources:** [S40](src.s40.md)

cause: `matcher` uses `,` as a separator on a version before v2.1.191; fix: Claude Code v2.1.191 or later treats `,` as a list separator like `/`. Earlier versions evaluate a comma as a literal character, so `"Edit,Write"` matches nothing. Use `/` instead, or upgrade Claude Code.
