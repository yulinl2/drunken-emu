---
id: hook.post-tool-batch
kind: hook
status: VERIFIED
title: "PostToolBatch"
sources: [S2]
---

# PostToolBatch

**Sources:** [S2](src.s2.md)

Fires after a parallel tool batch resolves, before the next model call. No matcher. Exit 2 stops the loop before the next model call. Top-level decision block applies.
