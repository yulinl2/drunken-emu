---
id: feature.remote-control-got-an-unexpected-server-response
kind: feature
status: VERIFIED
title: "\"Remote Control got an unexpected server response\""
sources: [S21]
---

# "Remote Control got an unexpected server response"

**Sources:** [S21](src.s21.md)

The Remote Control server accepted a request but replied in a form this version of Claude Code couldn't read, while creating the remote session or fetching its credentials. Retrying on the same version fails the same way. Run `claude update`, then run `/remote-control` to reconnect.
