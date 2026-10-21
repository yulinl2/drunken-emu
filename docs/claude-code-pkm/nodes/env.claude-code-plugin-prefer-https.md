---
id: env.claude-code-plugin-prefer-https
kind: env
status: VERIFIED
title: "CLAUDE_CODE_PLUGIN_PREFER_HTTPS"
sources: [S81]
---

# CLAUDE_CODE_PLUGIN_PREFER_HTTPS

**Sources:** [S81](src.s81.md)

Set to `1` to clone GitHub `owner/repo` shorthand sources over HTTPS instead of SSH. Applies to plugin install and update, and to `/plugin marketplace add` and `update`. Useful in CI runners, containers, or any environment without a configured SSH key for `github.com`
