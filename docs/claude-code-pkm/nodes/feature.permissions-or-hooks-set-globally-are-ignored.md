---
id: feature.permissions-or-hooks-set-globally-are-ignored
kind: feature
status: VERIFIED
title: "Permissions or hooks set globally are ignored"
sources: [S40]
---

# Permissions or hooks set globally are ignored

**Sources:** [S40](src.s40.md)

cause: Configuration was added to `~/.claude.json`; fix: `~/.claude.json` holds app state and UI toggles. `permissions`, `hooks`, and `env` belong in `~/.claude/settings.json`. These are two different files.
