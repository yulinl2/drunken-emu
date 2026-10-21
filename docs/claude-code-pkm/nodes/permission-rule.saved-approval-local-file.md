---
id: permission-rule.saved-approval-local-file
kind: permission-rule
status: VERIFIED
title: "Saved approvals write to the local file"
sources: [S3]
---

# Saved approvals write to the local file

**Sources:** [S3](src.s3.md)

Choosing "Yes, and don't ask again" on a Bash prompt saves an allow rule to .claude/settings.local.json. The CLI writes only to the local file. The VS Code approval card can choose the shared file instead.
