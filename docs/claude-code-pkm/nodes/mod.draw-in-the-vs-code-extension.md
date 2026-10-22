---
id: mod.draw-in-the-vs-code-extension
kind: mod
status: VERIFIED
title: "Draw in the VS Code extension"
sources: [S57]
---

# Draw in the VS Code extension

**Sources:** [S57](src.s57.md)

In the VS Code extension, what a mod draws appears in the chat panel with extension version 2.1.299 or later. A session that doesn't fetch feature flags, such as one on Amazon Bedrock, needs 2.1.304 or later. In a `ui.render` hook for the panel, `e.surface` is `vscode`. To check which sites and elements the panel draws, and which props it ignores, see the render sites and elements tables.
