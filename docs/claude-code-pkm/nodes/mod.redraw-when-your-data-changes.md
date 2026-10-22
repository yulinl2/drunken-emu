---
id: mod.redraw-when-your-data-changes
kind: mod
status: VERIFIED
title: "Redraw when your data changes"
sources: [S57]
---

# Redraw when your data changes

**Sources:** [S57](src.s57.md)

To have your sites drawn again after your own data changes, call `$.ui.invalidate('ui.render')`. This pane counts presses. The button's callback changes `count`, then asks for a redraw:
