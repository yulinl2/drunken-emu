---
id: feature.what-changes
kind: feature
status: VERIFIED
title: "What changes"
sources: [S75]
---

# What changes

**Sources:** [S75](src.s75.md)

Fullscreen rendering changes how the CLI draws to your terminal. The input box stays fixed at the bottom of the screen instead of moving as output streams in. If the input doesn't move while Claude is working, fullscreen rendering is active. Only visible messages are kept in the render tree, so memory stays constant regardless of conversation length.
