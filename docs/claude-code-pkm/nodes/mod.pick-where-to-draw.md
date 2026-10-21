---
id: mod.pick-where-to-draw
kind: mod
status: VERIFIED
title: "Pick where to draw"
sources: [S57]
---

# Pick where to draw

**Sources:** [S57](src.s57.md)

A `ui.render` hook runs for every render site unless you narrow it to the one you want to draw in. To choose the render site, pass a filter, called a matcher, as the second argument to `on`. `{ component: 'Pane' }` runs the hook only for panes. In the hook, `e.component` names the site, `e.surface` says which app is drawing, and `e.props` holds the site's own data. For a pane, `e.requestId` is the
