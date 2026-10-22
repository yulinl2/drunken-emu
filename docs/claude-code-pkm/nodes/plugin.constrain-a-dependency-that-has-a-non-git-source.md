---
id: plugin.constrain-a-dependency-that-has-a-non-git-source
kind: plugin
status: VERIFIED
title: "Constrain a dependency that has a non-git source"
sources: [S46]
---

# Constrain a dependency that has a non-git source

**Sources:** [S46](src.s46.md)

Tag-based resolution applies only to git-backed sources. For a dependency with an `npm`, `archive`, or `command` plugin source, the constraint doesn't control which version is fetched. It's still checked when the plugin loads, and the dependent plugin is disabled if the installed version doesn't satisfy it.
