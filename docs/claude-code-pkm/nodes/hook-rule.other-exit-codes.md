---
id: hook-rule.other-exit-codes
kind: hook-rule
status: VERIFIED
title: "Other exit codes"
sources: [S85]
---

# Other exit codes

**Sources:** [S85](src.s85.md)

A ` hook error` notice with `Failed with non-blocking status code:` means your hook's exit code wasn't 0 or 2 and its stdout was plain text or empty. Unless the hook is one whose failure blocks the action, this is a non-blocking error, so your hook didn't stop the action. To capture your hook's full stderr rather than the first line the notice shows, enable debug logging.
