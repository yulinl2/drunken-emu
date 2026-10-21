---
id: plugin.channels
kind: plugin
status: VERIFIED
title: "Channels"
sources: [S45]
---

# Channels

**Sources:** [S45](src.s45.md)

A channel lets an outside system such as a chat app send messages into a session. In a plugin, a channel is one of the MCP servers plus a `channels` entry that binds to it and can prompt for its own configuration. This manifest binds a channel to a `telegram` server and asks for a bot token:
