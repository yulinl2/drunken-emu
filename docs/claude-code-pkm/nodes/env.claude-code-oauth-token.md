---
id: env.claude-code-oauth-token
kind: env
status: VERIFIED
title: "CLAUDE_CODE_OAUTH_TOKEN"
sources: [S81]
---

# CLAUDE_CODE_OAUTH_TOKEN

**Sources:** [S81](src.s81.md)

OAuth access token for claude.ai authentication. Alternative to `/login` for SDK and automated environments. Takes precedence over keychain-stored credentials. Generate one with `claude setup-token`. Unless you run `/login`, Claude Code uses the token you set for the whole session. To replace an expired token, generate a new one and restart
