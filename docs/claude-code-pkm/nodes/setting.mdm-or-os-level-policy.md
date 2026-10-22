---
id: setting.mdm-or-os-level-policy
kind: setting
status: VERIFIED
title: "MDM or OS-level policy"
sources: [S61]
---

# MDM or OS-level policy

**Sources:** [S61](src.s61.md)

how you deliver it: As a macOS configuration profile or a Windows `HKLM` registry value, through Jamf, Intune, Group Policy, or a similar tool; see where each mechanism stores the policy; when claude code reads it: Read at startup and checked for changes every 30 minutes; use it when: You already manage devices with MDM or Group Policy
