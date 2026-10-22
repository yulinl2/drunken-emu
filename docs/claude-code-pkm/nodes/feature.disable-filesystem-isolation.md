---
id: feature.disable-filesystem-isolation
kind: feature
status: VERIFIED
title: "Disable filesystem isolation"
sources: [S68]
---

# Disable filesystem isolation

**Sources:** [S68](src.s68.md)

Set `sandbox.filesystem.disabled` to `true` to skip filesystem isolation while keeping network isolation. The example below turns off filesystem isolation while keeping an allowlist of network domains:
