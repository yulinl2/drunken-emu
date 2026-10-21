---
id: feature.settings-precedence
kind: feature
status: VERIFIED
title: "Settings precedence"
sources: [S62]
---

# Settings precedence

**Sources:** [S62](src.s62.md)

Server-managed settings and endpoint-managed settings both occupy the highest tier in the Claude Code settings hierarchy. A key you set here takes precedence over the same key in a user's own settings files or in a `--settings` value, apart from the exceptions to managed settings precedence.
