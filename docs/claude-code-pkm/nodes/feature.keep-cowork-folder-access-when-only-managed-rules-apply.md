---
id: feature.keep-cowork-folder-access-when-only-managed-rules-apply
kind: feature
status: VERIFIED
title: "Keep Cowork folder access when only managed rules apply"
sources: [S61]
---

# Keep Cowork folder access when only managed rules apply

**Sources:** [S61](src.s61.md)

Cowork in the Claude Desktop app runs its sessions on Claude Code and grants each session access to its working folders, such as the folder the user connects, through allow rules it supplies when it launches the session. When your managed policy sets `allowManagedPermissionRulesOnly`, Claude Code keeps only the allow rules in the managed policy: it drops allow rules a host supplies as parent setti
