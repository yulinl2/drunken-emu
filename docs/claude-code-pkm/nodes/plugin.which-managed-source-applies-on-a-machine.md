---
id: plugin.which-managed-source-applies-on-a-machine
kind: plugin
status: VERIFIED
title: "Which managed source applies on a machine"
sources: [S59]
---

# Which managed source applies on a machine

**Sources:** [S59](src.s59.md)

By default, only one of these three sources applies on a machine. Claude Code uses the first that delivers a policy key, checking server-managed settings first, then MDM policies, then the managed settings file. If server-managed settings deliver even one unrelated policy key, Claude Code ignores the plugin keys in an MDM policy or managed settings file on that machine, apart from the keys it read
