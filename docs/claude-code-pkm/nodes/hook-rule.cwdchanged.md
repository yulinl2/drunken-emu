---
id: hook-rule.cwdchanged
kind: hook-rule
status: VERIFIED
title: "CwdChanged"
sources: [S85]
---

# CwdChanged

**Sources:** [S85](src.s85.md)

Runs when a shell command in the main conversation changes the working directory, for example when Claude executes a `cd` command. Use this to react to directory changes: reload environment variables, activate project-specific toolchains, or run setup scripts automatically. Pairs with FileChanged for tools like direnv that manage per-directory environment.
