---
id: feature.when-an-injected-command-fails
kind: feature
status: VERIFIED
title: "When an injected command fails"
sources: [S32]
---

# When an injected command fails

**Sources:** [S32](src.s32.md)

A failed command aborts the entire skill invocation, not just its own placeholder. Claude never sees the skill content for that invocation. The abort shows `Shell command failed for pattern "..."`. The error message includes the command's output under `[stderr]`.
