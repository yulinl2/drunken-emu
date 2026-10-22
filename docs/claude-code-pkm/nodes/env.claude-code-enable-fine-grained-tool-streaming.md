---
id: env.claude-code-enable-fine-grained-tool-streaming
kind: env
status: VERIFIED
title: "CLAUDE_CODE_ENABLE_FINE_GRAINED_TOOL_STREAMING"
sources: [S81]
---

# CLAUDE_CODE_ENABLE_FINE_GRAINED_TOOL_STREAMING

**Sources:** [S81](src.s81.md)

Controls whether tool call inputs stream from the API as Claude generates them. With this off, a large tool input such as a long file write arrives only after Claude finishes generating it, which can look like it's hanging. Enabled by default on the Anthropic API. On Amazon Bedrock and Google Cloud's Agent Platform, enabled per model where the deployed container supports it. Set to `0` to opt out. Set to `1` to force on when routing through a proxy via `ANTHROPIC_BASE_URL`, `ANTHROPIC_VERTEX_BASE_URL`, or `ANTHROPIC_BEDROCK_BASE_URL`. Off by default on Microsoft Foundry and gateway connections
