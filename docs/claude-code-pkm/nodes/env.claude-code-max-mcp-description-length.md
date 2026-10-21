---
id: env.claude-code-max-mcp-description-length
kind: env
status: VERIFIED
title: "CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH"
sources: [S81]
---

# CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH

**Sources:** [S81](src.s81.md)

Maximum length in characters of MCP tool descriptions and MCP server instructions that Claude Code sends to the model. The value you set replaces both default limits: 4096, and 16384 for the description of a tool that Claude loads through tool search. Accepts a positive whole number in plain digits. Anything else is ignored and the defaults apply. Requires Claude Code v2.1.280 or later
