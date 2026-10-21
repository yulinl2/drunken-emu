---
id: hook.config-change
kind: hook
status: VERIFIED
title: "ConfigChange"
sources: [S2]
---

# ConfigChange

**Sources:** [S2](src.s2.md)

Fires when a config file changes during a session. Matchers: user_settings, project_settings, local_settings, policy_settings, skills. Exit 2 blocks the change, except for policy_settings.
