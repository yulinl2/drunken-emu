---
id: feature.mask-environment-variables
kind: feature
status: VERIFIED
title: "Mask environment variables"
sources: [S68]
---

# Mask environment variables

**Sources:** [S68](src.s68.md)

To mask an environment variable, set `"mode": "mask"` on its `credentials.envVars` entry. The command and anything it logs never hold the real credential, but its requests still authenticate. When the same variable is listed with `deny` in any scope, `deny` takes precedence.
