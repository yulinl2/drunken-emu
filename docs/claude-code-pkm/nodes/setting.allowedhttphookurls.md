---
id: setting.allowedhttphookurls
kind: setting
status: VERIFIED
title: "allowedHttpHookUrls"
sources: [S61]
---

# allowedHttpHookUrls

**Sources:** [S61](src.s61.md)

Claude Code enforces an empty managed allowlist until you fix the value, so an HTTP hook runs only if another settings file lists its URL. If only an individual entry is invalid, Claude Code strips that entry and enforces the rest.
