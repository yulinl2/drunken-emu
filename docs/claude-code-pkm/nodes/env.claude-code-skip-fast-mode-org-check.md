---
id: env.claude-code-skip-fast-mode-org-check
kind: env
status: VERIFIED
title: "CLAUDE_CODE_SKIP_FAST_MODE_ORG_CHECK"
sources: [S81]
---

# CLAUDE_CODE_SKIP_FAST_MODE_ORG_CHECK

**Sources:** [S81](src.s81.md)

Set to `1` to skip the client-side fast mode availability check, for proxies that intercept the check's request rather than refuse it. The API still rejects fast mode requests when your organization has fast mode disabled
