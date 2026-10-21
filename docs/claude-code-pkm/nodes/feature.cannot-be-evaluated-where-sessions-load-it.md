---
id: feature.cannot-be-evaluated-where-sessions-load-it
kind: feature
status: VERIFIED
title: "\"cannot be evaluated where sessions load it\""
sources: [S47]
---

# "cannot be evaluated where sessions load it"

**Sources:** [S47](src.s47.md)

You ran `claude plugin eval` in your shell with the name of a plugin installed from a marketplace you added from a local path. No session could load the plugin from that marketplace now, so the command refuses with this message and exits with code 1.
