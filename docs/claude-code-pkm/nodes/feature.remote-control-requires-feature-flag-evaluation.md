---
id: feature.remote-control-requires-feature-flag-evaluation
kind: feature
status: VERIFIED
title: "\"Remote Control requires feature-flag evaluation\""
sources: [S21]
---

# "Remote Control requires feature-flag evaluation"

**Sources:** [S21](src.s21.md)

An environment variable that turns off feature-flag evaluation is set, and the full message names the variable Claude Code found. On versions before 2.1.154, the same configuration produces "Remote Control is not yet enabled for your account" instead. What to do depends on the variable the message names:
