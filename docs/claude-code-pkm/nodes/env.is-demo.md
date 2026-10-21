---
id: env.is-demo
kind: env
status: VERIFIED
title: "IS_DEMO"
sources: [S81]
---

# IS_DEMO

**Sources:** [S81](src.s81.md)

Set to any non-empty value, such as `1`, to enable demo mode: hides your email and organization name from the header and `/status` output, and skips onboarding. Setting it to `0` or `false` still enables demo mode, unlike most on/off variables; unset the variable to turn it off. Useful when streaming or recording a session
