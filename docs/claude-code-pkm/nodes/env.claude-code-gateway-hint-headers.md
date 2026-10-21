---
id: env.claude-code-gateway-hint-headers
kind: env
status: VERIFIED
title: "CLAUDE_CODE_GATEWAY_HINT_HEADERS"
sources: [S81]
---

# CLAUDE_CODE_GATEWAY_HINT_HEADERS

**Sources:** [S81](src.s81.md)

Set to `1` to send the gateway hint headers, such as `x-claude-code-request-class` and `x-claude-code-compaction`, on a custom proxy or a third-party provider such as Amazon Bedrock or Claude Platform on AWS. Set to `0` to stop sending them on every connection, including a direct connection to the Anthropic API, where Claude Code sends them by default. Requires Claude Code v2.1.273 or later
