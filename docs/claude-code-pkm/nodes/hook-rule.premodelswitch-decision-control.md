---
id: hook-rule.premodelswitch-decision-control
kind: hook-rule
status: VERIFIED
title: "PreModelSwitch decision control"
sources: [S85]
---

# PreModelSwitch decision control

**Sources:** [S85](src.s85.md)

`PreModelSwitch` hooks can cancel the switch, ask the user to confirm it, or let it proceed. Exit code 2 or a top-level `decision: "block"` cancels the switch.
