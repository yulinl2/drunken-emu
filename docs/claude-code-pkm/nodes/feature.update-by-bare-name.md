---
id: feature.update-by-bare-name
kind: feature
status: VERIFIED
title: "Update by bare name"
sources: [S52]
---

# Update by bare name

**Sources:** [S52](src.s52.md)

You can pass a bare plugin name, which the command matches against your installed plugins. When installed plugins from different marketplaces share the name, the command refuses the update and lists the qualified `plugin-name@marketplace-name` commands to run instead. Updating by bare name requires Claude Code v2.1.246 or later.
