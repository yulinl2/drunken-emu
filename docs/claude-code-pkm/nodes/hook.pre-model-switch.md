---
id: hook.pre-model-switch
kind: hook
status: VERIFIED
title: "PreModelSwitch"
sources: [S2]
---

# PreModelSwitch

**Sources:** [S2](src.s2.md)

Fires before a requested model switch applies. Matcher: canonical model name. Can block with exit 2, a permissionDecision of deny, or a top-level decision block. A timeout blocks the switch.
