---
id: plugin.git-subdir-plugin-source
kind: plugin
status: VERIFIED
title: "git-subdir plugin source"
sources: [S51]
---

# git-subdir plugin source

**Sources:** [S51](src.s51.md)

`url` accepts a full git URL or GitHub `owner/repo` shorthand. `path` is the subdirectory that holds the plugin, and Claude Code checks out only that subdirectory. Over an `https` or SSH URL, Claude Code asks the server for a partial clone, so from a host that supports partial clones, a plugin in a large monorepo installs without downloading the rest of the repository.
