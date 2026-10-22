---
id: mod.set-a-hotkey-and-the-first-focus
kind: mod
status: VERIFIED
title: "Set a hotkey and the first focus"
sources: [S57]
---

# Set a hotkey and the first focus

**Sources:** [S57](src.s57.md)

`hotkey`: to let the user press a `Button` with one key, give it a `hotkey` of one digit or one lowercase letter, as in `hotkey: 'a'` `autoFocus`: to choose which control has the focus when the pane opens, add `autoFocus: true` to it. In the VS Code extension, `autoFocus` does nothing: the control draws as if you had left it out, and you don't need to change anything. The prop accepts only `true`,
