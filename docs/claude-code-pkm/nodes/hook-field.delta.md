---
id: hook-field.delta
kind: hook-field
status: VERIFIED
title: "delta"
sources: [S85]
---

# delta

**Sources:** [S85](src.s85.md)

The newly completed lines since the prior batch, terminating newlines included. Always whole lines, except the final batch which may end mid-line. In interactive runs, the final batch's delta is empty when the message ends on a newline, so treat `final`, not a non-empty delta, as the end-of-message signal. In Agent SDK and `claude -p` runs, the single call carries the entire message
