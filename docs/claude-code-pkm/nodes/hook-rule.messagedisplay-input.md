---
id: hook-rule.messagedisplay-input
kind: hook-rule
status: VERIFIED
title: "MessageDisplay input"
sources: [S85]
---

# MessageDisplay input

**Sources:** [S85](src.s85.md)

In addition to the common input fields, MessageDisplay hooks receive identifiers for the turn and message, the position of this call within the message, and the new text in `delta`. Batch boundaries depend on how the text streams, so use `index` and `final` to track progress through a message rather than expecting lines to be grouped a particular way.
