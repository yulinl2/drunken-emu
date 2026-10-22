---
id: setting.managed-invalid-entries
kind: setting
status: VERIFIED
title: "Broken managed entries"
sources: [S3]
---

# Broken managed entries

**Sources:** [S3](src.s3.md)

Claude Code keeps enforcing the rest of a managed file, drops the invalid entries, and falls back to stricter values for the affected keys until they are fixed.
