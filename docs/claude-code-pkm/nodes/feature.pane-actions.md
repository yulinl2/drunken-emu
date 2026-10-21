---
id: feature.pane-actions
kind: feature
status: VERIFIED
title: "Pane actions"
sources: [S79]
---

# Pane actions

**Sources:** [S79](src.s79.md)

Actions for a pane drawn by a mod. The scroll, resize, and close actions apply in the `Pane` context. `pane:close` also applies in the `PaneField` context, so it works while one of the pane's fields has focus. `pane:next` and `pane:previous` apply in the `Global` context while more than one pane is open.
