---
id: hook-field.headers
kind: hook-field
status: VERIFIED
title: "headers"
sources: [S85]
---

# headers

**Sources:** [S85](src.s85.md)

Additional HTTP headers as key-value pairs. Values support environment variable interpolation using `$VAR_NAME` or `${VAR_NAME}` syntax. Only variables listed in `allowedEnvVars` are resolved (required: no)
