---
id: env.claude-code-disable-bedrock-content-type-default
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_BEDROCK_CONTENT_TYPE_DEFAULT"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_BEDROCK_CONTENT_TYPE_DEFAULT

**Sources:** [S81](src.s81.md)

Set to `1` to stop Claude Code from treating an Amazon Bedrock streaming response with a missing or empty `Content-Type` header as Amazon Bedrock's binary event stream. By default, Claude Code assumes a gateway dropped the header from an otherwise unmodified response, so it decodes the body and streaming keeps working. Set this only for a gateway that also re-emits the stream as server-sent events; Claude Code then reads the header-less body as server-sent events instead. Requires Claude Code v2.1.239 or later
