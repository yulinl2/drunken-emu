---
id: mod.when-claude-code-redraws-without-being-asked
kind: mod
status: VERIFIED
title: "When Claude Code redraws without being asked"
sources: [S57]
---

# When Claude Code redraws without being asked

**Sources:** [S57](src.s57.md)

Claude Code runs your `ui.render` hook again when the site's props change or the terminal's width changes. When a `Client` in the site fails and your mod handles `ui.fault`, Claude Code runs the hook once more after your `ui.fault` hooks return, so your `ui.render` hook can leave the `Client` out. It doesn't run the hook on a timer, and it can't tell when a variable in your module changes.
