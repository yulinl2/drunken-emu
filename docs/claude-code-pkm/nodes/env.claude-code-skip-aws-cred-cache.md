---
id: env.claude-code-skip-aws-cred-cache
kind: env
status: VERIFIED
title: "CLAUDE_CODE_SKIP_AWS_CRED_CACHE"
sources: [S81]
---

# CLAUDE_CODE_SKIP_AWS_CRED_CACHE

**Sources:** [S81](src.s81.md)

Set to `1` to turn off the in-process cache of credentials resolved from the AWS default credential provider chain, so Claude Code resolves the chain on every API request. With the cache off, an SSO-backed profile requests credentials from IAM Identity Center on every request. See credential caching and resolution timeout. Requires Claude Code v2.1.207 or later
