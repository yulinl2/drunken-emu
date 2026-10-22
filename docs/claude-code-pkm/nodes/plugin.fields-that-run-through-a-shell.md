---
id: plugin.fields-that-run-through-a-shell
kind: plugin
status: VERIFIED
title: "Fields that run through a shell"
sources: [S50]
---

# Fields that run through a shell

**Sources:** [S50](src.s50.md)

Shell-form hook commands, monitor commands, and MCP `headersHelper` reject `${user_config.*}`. A component that references it in one of these fields fails with an error instead of running, because the field's value is passed to a shell that would re-parse the substituted value.
