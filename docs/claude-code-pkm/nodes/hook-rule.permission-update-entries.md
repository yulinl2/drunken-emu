---
id: hook-rule.permission-update-entries
kind: hook-rule
status: VERIFIED
title: "Permission update entries"
sources: [S85]
---

# Permission update entries

**Sources:** [S85](src.s85.md)

The `updatedPermissions` output field and the `permission_suggestions` input field both use the same array of entry objects. Each entry has a `type` that determines its other fields, and a `destination` that controls where the change is written.
