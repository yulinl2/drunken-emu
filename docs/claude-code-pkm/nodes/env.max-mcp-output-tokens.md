---
id: env.max-mcp-output-tokens
kind: env
status: VERIFIED
title: "MAX_MCP_OUTPUT_TOKENS"
sources: [S81]
---

# MAX_MCP_OUTPUT_TOKENS

**Sources:** [S81](src.s81.md)

Maximum number of tokens allowed in MCP tool responses (default: 25000). Claude Code displays a warning when output exceeds 10,000 tokens. Tools that declare `anthropic/maxResultSizeChars` use that character limit for text content instead, but image content from those tools is still subject to this variable. A successful text result longer than 50,000 characters from a tool without that annotation is saved to a file regardless of this variable
