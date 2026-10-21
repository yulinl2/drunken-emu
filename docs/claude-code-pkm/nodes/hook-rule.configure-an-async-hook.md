---
id: hook-rule.configure-an-async-hook
kind: hook-rule
status: VERIFIED
title: "Configure an async hook"
sources: [S85]
---

# Configure an async hook

**Sources:** [S85](src.s85.md)

Add `"async": true` to a command hook's configuration to run it in the background without blocking Claude. This field is only available on `type: "command"` hooks.
