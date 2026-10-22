---
id: feature.compose-every-managed-source
kind: feature
status: VERIFIED
title: "Compose every managed source"
sources: [S61]
---

# Compose every managed source

**Sources:** [S61](src.s61.md)

To have Claude Code apply every admin source your organization delivers, set `managedSourcesBehavior` to `"merge"` in the highest-ranked source you deploy. Claude Code reads the key only from the highest-ranked source that carries either the key or a policy key, so a lower source can't opt itself into merging with the source above it, and a machine that never receives server-managed settings needs
