---
id: feature.protect-credentials
kind: feature
status: VERIFIED
title: "Protect credentials"
sources: [S68]
---

# Protect credentials

**Sources:** [S68](src.s68.md)

The `sandbox.credentials` setting declares credential files and environment variables to protect from sandboxed commands. Each entry names a file path or an environment variable and a `mode`. The dedicated `credentials` block keeps credential rules grouped together and separate from general filesystem rules.
