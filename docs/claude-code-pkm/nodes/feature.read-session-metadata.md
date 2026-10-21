---
id: feature.read-session-metadata
kind: feature
status: VERIFIED
title: "Read session metadata"
sources: [S38]
---

# Read session metadata

**Sources:** [S38](src.s38.md)

The `system/init` event reports session metadata including the model, tools, MCP servers, and loaded plugins. It is the first event in the stream unless startup events precede it:
