---
id: mod.add-a-tool
kind: mod
status: VERIFIED
title: "Add a tool"
sources: [S56]
---

# Add a tool

**Sources:** [S56](src.s56.md)

A tool is for Claude. Register it with a name, a description Claude reads, and a JSON Schema for its input. Claude sees it under a longer name made of `mcp`, your plugin's name, two underscores, and the name you registered. You handle its calls in a `tool.call` hook filtered to that full name. This example, from a plugin named `my-mod`, registers `ticket`, so the full name is `mcpmy-modticket`. It
