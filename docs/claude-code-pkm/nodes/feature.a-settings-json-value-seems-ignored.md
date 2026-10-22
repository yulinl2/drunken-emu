---
id: feature.a-settings-json-value-seems-ignored
kind: feature
status: VERIFIED
title: "A settings.json value seems ignored"
sources: [S40]
---

# A settings.json value seems ignored

**Sources:** [S40](src.s40.md)

cause: The same key is set in `settings.local.json`; fix: `settings.local.json` overrides `settings.json`, and both override `~/.claude/settings.json`. See settings precedence.
