---
id: feature.cleanup-logic-never-runs-at-session-end
kind: feature
status: VERIFIED
title: "Cleanup logic never runs at session end"
sources: [S40]
---

# Cleanup logic never runs at session end

**Sources:** [S40](src.s40.md)

cause: No `SessionEnd` hook configured; fix: Add a `SessionEnd` hook in `settings.json`. See the hook events list.
