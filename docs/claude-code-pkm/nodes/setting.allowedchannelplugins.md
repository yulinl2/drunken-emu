---
id: setting.allowedchannelplugins
kind: setting
status: VERIFIED
title: "allowedChannelPlugins"
sources: [S61]
---

# allowedChannelPlugins

**Sources:** [S61](src.s61.md)

Claude Code enforces an empty allowlist until you fix the value, so no channel plugin passed to `--channels` is admitted. If only an individual entry is invalid, it strips that entry and enforces the rest.
