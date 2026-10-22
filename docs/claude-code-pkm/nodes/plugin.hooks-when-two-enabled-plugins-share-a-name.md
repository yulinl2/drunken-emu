---
id: plugin.hooks-when-two-enabled-plugins-share-a-name
kind: plugin
status: VERIFIED
title: "Hooks when two enabled plugins share a name"
sources: [S49]
---

# Hooks when two enabled plugins share a name

**Sources:** [S49](src.s49.md)

When you install and enable two plugins with the same manifest name from different marketplaces, both appear as enabled in `/plugin`, but the hooks of one of them are left out. One plugin per name registers the hooks in its `hooks/hooks.json`, and one plugin per name loads a hooks module. When your organization's managed settings turn on one of the copies, that copy holds the name. Otherwise the c
