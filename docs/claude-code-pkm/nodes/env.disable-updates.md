---
id: env.disable-updates
kind: env
status: VERIFIED
title: "DISABLE_UPDATES"
sources: [S81]
---

# DISABLE_UPDATES

**Sources:** [S81](src.s81.md)

Set to `1` to block all updates including manual `claude update` and `claude install`. Stricter than `DISABLE_AUTOUPDATER`. Use when distributing Claude Code through your own channels and users should not self-update
