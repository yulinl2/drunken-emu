---
id: hook.session-end
kind: hook
status: VERIFIED
title: "SessionEnd"
sources: [S2]
---

# SessionEnd

**Sources:** [S2](src.s2.md)

Fires when a session terminates. Matchers: clear, resume, logout, prompt_input_exit, other. Exit 2 shows stderr to the user only. Shares a 1.5 s budget, raised to match a longer per-hook timeout of up to 60 s ([Default timeouts](hook-rule.timeout-defaults.md)).
