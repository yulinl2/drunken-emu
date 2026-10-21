---
id: env.claude-code-propagate-traceparent
kind: env
status: VERIFIED
title: "CLAUDE_CODE_PROPAGATE_TRACEPARENT"
sources: [S81]
---

# CLAUDE_CODE_PROPAGATE_TRACEPARENT

**Sources:** [S81](src.s81.md)

Set to `1` to propagate W3C trace context when `ANTHROPIC_BASE_URL` points at a custom proxy. Propagation covers the `traceparent` header on model and HTTP MCP requests and the `TRACEPARENT` environment variable for Bash, PowerShell, and hook subprocesses. By default, propagation is enabled only when connected directly to the Anthropic API. Added in v2.1.152. See Traces (beta)
