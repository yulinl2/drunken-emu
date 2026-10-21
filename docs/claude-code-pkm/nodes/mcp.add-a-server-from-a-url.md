---
id: mcp.add-a-server-from-a-url
kind: mcp
status: VERIFIED
title: "Add a server from a URL"
sources: [S31]
---

# Add a server from a URL

**Sources:** [S31](src.s31.md)

A URL means the server is remote. For an `https://` endpoint, add it with `--transport http`, or follow Option 2 when the instructions say the endpoint uses SSE. For a `wss://` endpoint, use Option 4 instead, since `--transport` doesn't accept `ws`:
