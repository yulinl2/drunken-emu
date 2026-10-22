---
id: feature.keys-that-fail-closed
kind: feature
status: VERIFIED
title: "Keys that fail closed"
sources: [S61]
---

# Keys that fail closed

**Sources:** [S61](src.s61.md)

When a managed source sets a top-level key that has a single restrictive value, such as `allowManagedPermissionRulesOnly`, `disableAutoMode`, or `skipDangerousModePermissionPrompt`, to something Claude Code can't read, the key reads as that value until you fix it. The report says the key `was present but invalid` and names the value Claude Code treats it as. For a key inside `sandbox`, see Invalid
