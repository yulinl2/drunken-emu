---
id: env.claude-code-aws-chain-resolve-timeout-ms
kind: env
status: VERIFIED
title: "CLAUDE_CODE_AWS_CHAIN_RESOLVE_TIMEOUT_MS"
sources: [S81]
---

# CLAUDE_CODE_AWS_CHAIN_RESOLVE_TIMEOUT_MS

**Sources:** [S81](src.s81.md)

Time in milliseconds Claude Code waits for the AWS default credential provider chain to produce credentials before the request fails with `AWS default-chain credential resolve timed out` (default: `60000`). Raise it when a step in your chain legitimately needs longer, such as a browser-based SSO sign-in with MFA through a wrapper like `aws-vault`. Applies on Amazon Bedrock, Claude Platform on AWS, and the Mantle endpoint. See credential caching and resolution timeout. Requires Claude Code v2.1.207 or later
