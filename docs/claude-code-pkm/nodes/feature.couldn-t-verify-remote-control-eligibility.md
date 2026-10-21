---
id: feature.couldn-t-verify-remote-control-eligibility
kind: feature
status: VERIFIED
title: "\"Couldn't verify Remote Control eligibility\""
sources: [S21]
---

# "Couldn't verify Remote Control eligibility"

**Sources:** [S21](src.s21.md)

Claude Code could not reach the feature-flag service to check whether Remote Control is enabled for your account, typically because you are offline or a proxy is blocking the request. Retry once you have network access, or run `claude doctor` for details. The related message "Couldn't verify your organization's Remote Control policy" means Claude Code hit an error reading that policy, and has the
