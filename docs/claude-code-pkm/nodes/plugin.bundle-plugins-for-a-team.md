---
id: plugin.bundle-plugins-for-a-team
kind: plugin
status: VERIFIED
title: "Bundle plugins for a team"
sources: [S46]
---

# Bundle plugins for a team

**Sources:** [S46](src.s46.md)

To let engineers install a curated set of plugins with one command, publish a plugin whose manifest contains a `name` and a `dependencies` array. A plugin manifest needs only `name`, so this is a valid plugin, and installing it installs every dependency.
