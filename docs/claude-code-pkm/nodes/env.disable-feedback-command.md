---
id: env.disable-feedback-command
kind: env
status: VERIFIED
title: "DISABLE_FEEDBACK_COMMAND"
sources: [S81]
---

# DISABLE_FEEDBACK_COMMAND

**Sources:** [S81](src.s81.md)

Set to `1` to disable the `/feedback` command and Claude-drafted feedback. Also disables `/bug` and `/share`, which report through the same path; before v2.1.212 they were aliases of `/feedback`, so the command was disabled under every name. The older name `DISABLE_BUG_COMMAND` is also accepted
