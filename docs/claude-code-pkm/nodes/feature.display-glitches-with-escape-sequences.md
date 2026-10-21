---
id: feature.display-glitches-with-escape-sequences
kind: feature
status: VERIFIED
title: "Display glitches with escape sequences"
sources: [S78]
---

# Display glitches with escape sequences

**Sources:** [S78](src.s78.md)

Complex escape sequences (ANSI colors, OSC 8 links) can occasionally cause garbled output if they overlap with other UI updates. Multi-line status lines with escape codes are more prone to rendering issues than single-line plain text.
