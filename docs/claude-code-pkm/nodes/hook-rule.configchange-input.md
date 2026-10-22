---
id: hook-rule.configchange-input
kind: hook-rule
status: VERIFIED
title: "ConfigChange input"
sources: [S85]
---

# ConfigChange input

**Sources:** [S85](src.s85.md)

In addition to the common input fields, ConfigChange hooks receive `source` and optionally `file_path`. The `source` field indicates which configuration type changed, and `file_path` provides the path to the specific file that was modified.
