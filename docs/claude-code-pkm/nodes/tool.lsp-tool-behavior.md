---
id: tool.lsp-tool-behavior
kind: tool
status: VERIFIED
title: "LSP tool behavior"
sources: [S82]
---

# LSP tool behavior

**Sources:** [S82](src.s82.md)

The LSP tool gives Claude code intelligence from a running language server. After each file edit, it automatically reports type errors and warnings so Claude can fix issues without a separate build step. Claude can also call it directly to navigate code:
