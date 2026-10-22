---
id: feature.mask-credential-files
kind: feature
status: VERIFIED
title: "Mask credential files"
sources: [S68]
---

# Mask credential files

**Sources:** [S68](src.s68.md)

To mask a credential file, set `"mode": "mask"` on its `credentials.files` entry. Masking files requires Claude Code v2.1.221 or later. What a sandboxed command sees depends on the platform:
