---
id: plugin.depend-on-a-plugin-from-another-marketplace
kind: plugin
status: VERIFIED
title: "Depend on a plugin from another marketplace"
sources: [S46]
---

# Depend on a plugin from another marketplace

**Sources:** [S46](src.s46.md)

By default, Claude Code doesn't install a dependency from a different marketplace than the declaring plugin's own, unless the user already has that dependency installed and enabled at the same scope. This default prevents one marketplace from silently installing plugins from a source the user hasn't reviewed.
