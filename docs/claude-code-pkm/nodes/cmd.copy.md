---
id: cmd.copy
kind: command
status: VERIFIED
title: "/copy"
sources: [S80]
---

# /copy

**Sources:** [S80](src.s80.md)

Copy the last assistant response to clipboard. Pass a number `N` to copy the Nth-latest response: `/copy 2` copies the second-to-last. When code blocks or blockquotes are present, shows an interactive picker to select individual blocks or the full response. Press `w` in the picker to write the selection to a file instead of the clipboard, which is useful over SSH
