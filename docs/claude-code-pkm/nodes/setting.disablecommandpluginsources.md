---
id: setting.disablecommandpluginsources
kind: setting
status: VERIFIED
title: "disableCommandPluginSources"
sources: [S61]
---

# disableCommandPluginSources

**Sources:** [S61](src.s61.md)

When `true`, blocks `command` plugin sources entirely, so the marketplace-declared command never runs. Also blocks marketplace `headersHelper` commands, except for a marketplace that managed settings themselves declare. When unset, follows `allowManagedHooksOnly`. Requires Claude Code v2.1.229 or later, and the `headersHelper` block requires v2.1.238 or later
