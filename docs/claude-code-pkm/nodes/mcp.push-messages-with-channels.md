---
id: mcp.push-messages-with-channels
kind: mcp
status: VERIFIED
title: "Push messages with channels"
sources: [S31]
---

# Push messages with channels

**Sources:** [S31](src.s31.md)

An MCP server can also push messages directly into your session so Claude can react to external events like CI results, monitoring alerts, or chat messages. To enable this, your server declares the `claude/channel` capability and you opt it in with the `--channels` flag at startup. See Channels to use an officially supported channel, or Channels reference to build your own.
