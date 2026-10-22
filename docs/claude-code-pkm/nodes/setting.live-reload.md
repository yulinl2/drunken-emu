---
id: setting.live-reload
kind: setting
status: VERIFIED
title: "Live reload of settings"
sources: [S3]
---

# Live reload of settings

**Sources:** [S3](src.s3.md)

Claude Code watches settings files and reloads them. Edits to permissions, hooks and apiKeyHelper apply to the running session without a restart. A settings file created mid-session loads if its folder existed at start; a .claude folder created in the same session also loads. Some keys are read only at start. The hook case conflicts with repo observations: [Q1: Does a hook added mid-session take effect?](question.q1.md).

## Linked from

- [Observation: mid-session hook had no effect](obs.hook-mid-session-no-effect.md)
- [Q1: Does a hook added mid-session take effect?](question.q1.md)
