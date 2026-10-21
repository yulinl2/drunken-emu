---
id: feature.pbcopy-xclip-or-wl-copy-doesn-t-update-the-clipboard
kind: feature
status: VERIFIED
title: "pbcopy, xclip, or wl-copy doesn't update the clipboard"
sources: [S68]
---

# pbcopy, xclip, or wl-copy doesn't update the clipboard

**Sources:** [S68](src.s68.md)

The `pbcopy`, `xclip`, and `wl-copy` clipboard utilities can fail to reach the system clipboard from inside the sandbox, in which case the text piped to them doesn't arrive.
