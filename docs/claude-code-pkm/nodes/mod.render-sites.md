---
id: mod.render-sites
kind: mod
status: VERIFIED
title: "Render sites"
sources: [S54]
---

# Render sites

**Sources:** [S54](src.s54.md)

A render site is an extension point in Claude Code's interface. Each row is a value of `e.component` in a `ui.render` hook, with the fields of `e.props` and the apps that render it. `e.surface` names the app that's drawing, such as `terminal`, `desktop`, or `vscode`. Change what Claude Code already draws shows what a hook can do at a site, with an example of each choice.
