---
id: mod.ui-invalidate-ui-render-redraws
kind: mod
status: VERIFIED
title: "$.ui.invalidate('ui.render') redraws"
sources: [S54]
---

# $.ui.invalidate('ui.render') redraws

**Sources:** [S54](src.s54.md)

value: Throttled to 10 a second, or 30 in the terminal for the visible pane, the expanded band, and the hint line under the prompt. Calls that come sooner are coalesced.
