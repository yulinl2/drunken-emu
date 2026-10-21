---
id: env.claude-code-disable-auth-refresh-lock
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_AUTH_REFRESH_LOCK"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_AUTH_REFRESH_LOCK

**Sources:** [S81](src.s81.md)

Set to `1` to make a Claude Code process run its `gcpAuthRefresh` or `awsAuthRefresh` command itself instead of waiting while another process runs it. Requires Claude Code v2.1.286 or later
