---
id: hook-rule.configchange-decision-control
kind: hook-rule
status: VERIFIED
title: "ConfigChange decision control"
sources: [S85]
---

# ConfigChange decision control

**Sources:** [S85](src.s85.md)

ConfigChange hooks can block configuration changes from taking effect. Use exit code 2 or a JSON `decision` to prevent the change. When blocked, the new settings are not applied to the running session.
