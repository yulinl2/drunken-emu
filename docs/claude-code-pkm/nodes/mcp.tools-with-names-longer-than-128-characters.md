---
id: mcp.tools-with-names-longer-than-128-characters
kind: mcp
status: VERIFIED
title: "Tools with names longer than 128 characters"
sources: [S31]
---

# Tools with names longer than 128 characters

**Sources:** [S31](src.s31.md)

If `/mcp` lists a tool that Claude can't call, check whether the tool's full name is longer than 128 characters. Run `/mcp` in your session and select the tool to see its full name, such as `mcp`. Claude Code leaves an MCP tool out of the tools it sends to Claude when its full name is over 128 characters. The Claude API rejects a request that includes such a tool, so leaving the tool out keeps the
