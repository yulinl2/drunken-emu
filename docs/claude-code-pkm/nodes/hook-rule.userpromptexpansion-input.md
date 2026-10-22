---
id: hook-rule.userpromptexpansion-input
kind: hook-rule
status: VERIFIED
title: "UserPromptExpansion input"
sources: [S85]
---

# UserPromptExpansion input

**Sources:** [S85](src.s85.md)

In addition to the common input fields, UserPromptExpansion hooks receive `expansion_type`, `command_name`, `command_args`, `command_source`, and the original `prompt` string. The `expansion_type` field is `slash_command` for skill and custom commands, or `mcp_prompt` for MCP server prompts.
