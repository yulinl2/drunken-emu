---
id: feature.remote-control-requires-a-full-scope-login-token
kind: feature
status: VERIFIED
title: "\"Remote Control requires a full-scope login token\""
sources: [S21]
---

# "Remote Control requires a full-scope login token"

**Sources:** [S21](src.s21.md)

You're authenticated with a long-lived token from `claude setup-token` or the `CLAUDE_CODE_OAUTH_TOKEN` environment variable. These tokens can only make model requests, so they can't establish Remote Control sessions. Run `claude auth login` to authenticate with a full-scope session token instead.
