---
id: plugin.release-a-plugin-that-others-depend-on
kind: plugin
status: VERIFIED
title: "Release a plugin that others depend on"
sources: [S46]
---

# Release a plugin that others depend on

**Sources:** [S46](src.s46.md)

If you maintain a plugin that other plugins depend on with a version constraint, tag its releases so those constraints can resolve. A constraint resolves against git tags on the repository that hosts the plugin. Tag the repository that the plugin's plugin source in `marketplace.json` points at:
