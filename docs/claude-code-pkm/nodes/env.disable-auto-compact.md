---
id: env.disable-auto-compact
kind: env
status: VERIFIED
title: "DISABLE_AUTO_COMPACT"
sources: [S81]
---

# DISABLE_AUTO_COMPACT

**Sources:** [S81](src.s81.md)

Set to `1` to disable automatic compaction when approaching the context limit, along with idle compaction. The manual `/compact` command remains available. Use when you want explicit control over when compaction occurs. Overrides the `autoCompactEnabled` setting
