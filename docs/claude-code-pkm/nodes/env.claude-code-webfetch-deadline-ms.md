---
id: env.claude-code-webfetch-deadline-ms
kind: env
status: VERIFIED
title: "CLAUDE_CODE_WEBFETCH_DEADLINE_MS"
sources: [S81]
---

# CLAUDE_CODE_WEBFETCH_DEADLINE_MS

**Sources:** [S81](src.s81.md)

Upper bound in milliseconds on how long WebFetch waits for a page to download, including any redirects it follows. A download that hasn't completed by then fails with a deadline error. The default is `300000`, which is five minutes. Set to `0` to remove the limit. Takes plain digits only; a decimal or any other spelling keeps the default. Requires Claude Code v2.1.268 or later
