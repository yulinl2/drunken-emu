---
id: feature.invalid-entries-in-delivered-settings
kind: feature
status: VERIFIED
title: "Invalid entries in delivered settings"
sources: [S62]
---

# Invalid entries in delivered settings

**Sources:** [S62](src.s62.md)

When part of a payload fails schema validation, Claude Code surfaces a validation error and applies every remaining valid setting; Invalid entries in managed settings says what it drops and which keys fall back to a stricter value. Requires Claude Code v2.1.169 or later.
