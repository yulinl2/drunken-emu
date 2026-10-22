---
id: plugin.combine-constraints-from-several-plugins
kind: plugin
status: VERIFIED
title: "Combine constraints from several plugins"
sources: [S46]
---

# Combine constraints from several plugins

**Sources:** [S46](src.s46.md)

When several installed plugins constrain the same dependency, the dependency resolves to the highest version that satisfies all of their ranges. Common combinations resolve like this:
