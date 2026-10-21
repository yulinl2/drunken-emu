---
id: mod.hold-toasts-behind-a-dialog
kind: mod
status: VERIFIED
title: "Hold toasts behind a dialog"
sources: [S57]
---

# Hold toasts behind a dialog

**Sources:** [S57](src.s57.md)

Pass `holdToasts: true` to `$.ui.open` when the pane is a dialog the user answers and leaves, so toasts don't appear while they decide. In the terminal, the hold lasts while that pane is the one showing, and a toast raised in that time waits until the hold ends.
