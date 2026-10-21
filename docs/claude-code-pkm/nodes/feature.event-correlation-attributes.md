---
id: feature.event-correlation-attributes
kind: feature
status: VERIFIED
title: "Event correlation attributes"
sources: [S65]
---

# Event correlation attributes

**Sources:** [S65](src.s65.md)

When a user submits a prompt, Claude Code may make multiple API calls and run several tools. The `prompt.id` attribute lets you tie all of those events back to the single prompt that triggered them.
