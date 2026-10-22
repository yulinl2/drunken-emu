---
id: env.claude-code-disable-bedrock-content-type-guard
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_BEDROCK_CONTENT_TYPE_GUARD"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_BEDROCK_CONTENT_TYPE_GUARD

**Sources:** [S81](src.s81.md)

Set to `1` to skip the check that an Amazon Bedrock streaming response carries the `application/vnd.amazon.eventstream` content-type. Without this variable, when a response carries a different content-type, Claude Code fails the request with an error naming that type, which means a gateway or proxy is transforming the response. Configure the gateway to forward the `Content-Type` header and body unmodified rather than setting this variable. Requires Claude Code v2.1.208 or later
