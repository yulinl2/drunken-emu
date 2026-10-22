---
id: hook-rule.run-hooks-in-the-background
kind: hook-rule
status: VERIFIED
title: "Run hooks in the background"
sources: [S85]
---

# Run hooks in the background

**Sources:** [S85](src.s85.md)

By default, hooks block Claude's execution until they complete. For long-running tasks like deployments, test suites, or external API calls, set `"async": true` to run the hook in the background while Claude continues working. Async hooks can't block or control Claude's behavior: response fields like `decision`, `permissionDecision`, and `continue` have no effect, because the action they would hav
