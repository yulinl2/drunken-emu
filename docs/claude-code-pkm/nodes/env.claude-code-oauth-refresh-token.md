---
id: env.claude-code-oauth-refresh-token
kind: env
status: VERIFIED
title: "CLAUDE_CODE_OAUTH_REFRESH_TOKEN"
sources: [S81]
---

# CLAUDE_CODE_OAUTH_REFRESH_TOKEN

**Sources:** [S81](src.s81.md)

OAuth refresh token for Claude.ai authentication. When set, `claude auth login` exchanges this token directly instead of opening a browser. Requires `CLAUDE_CODE_OAUTH_SCOPES`. Useful for provisioning authentication in automated environments
