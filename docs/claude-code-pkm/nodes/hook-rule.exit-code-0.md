---
id: hook-rule.exit-code-0
kind: hook-rule
status: VERIFIED
title: "Exit code 0"
sources: [S85]
---

# Exit code 0

**Sources:** [S85](src.s85.md)

Exit 0 means success, and is the intended exit code when you print JSON for structured control. When your hook exits 0 but prints JSON that can't be parsed or fails schema validation, the action goes ahead unless the hook is one whose failure blocks the action. Instead of a success with your fields applied, the run is a non-blocking error.
