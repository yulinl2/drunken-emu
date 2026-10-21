---
id: setting.file-based
kind: setting
status: VERIFIED
title: "File-based"
sources: [S61]
---

# File-based

**Sources:** [S61](src.s61.md)

how you deliver it: As `managed-settings.json` in a system directory on each machine; see where each mechanism stores the policy; when claude code reads it: Read at startup and reloaded when a file changes; use it when: Machines without MDM, Linux hosts, or images you build yourself
