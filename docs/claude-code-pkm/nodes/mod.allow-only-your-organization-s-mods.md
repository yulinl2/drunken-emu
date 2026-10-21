---
id: mod.allow-only-your-organization-s-mods
kind: mod
status: VERIFIED
title: "Allow only your organization's mods"
sources: [S58]
---

# Allow only your organization's mods

**Sources:** [S58](src.s58.md)

To run your organization's mods and block the ones users bring, deploy the settings from the Only your organization's mods row of the policy table, plus `disableSideloadFlags`. With this complete `managed-settings.json`, Claude Code refuses users' own mods, so none of their hooks run, and your policy mod runs ahead of other mods:
