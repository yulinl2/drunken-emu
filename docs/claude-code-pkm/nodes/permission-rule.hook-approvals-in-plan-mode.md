---
id: permission-rule.hook-approvals-in-plan-mode
kind: permission-rule
status: VERIFIED
title: "Hook approvals in plan mode"
sources: [S66]
---

# Hook approvals in plan mode

**Sources:** [S66](src.s66.md)

In plan mode, apart from `ExitPlanMode`, your `PreToolUse` hook's `"allow"` has no effect on a file edit or another call that isn't read-only. You get the same prompt, block, or approval the call would get with no hook, and Claude Code still applies any `updatedInput` the hook returns. If the hook answers `ExitPlanMode` with `"allow"` and `updatedInput`, that tool still runs without a prompt.
