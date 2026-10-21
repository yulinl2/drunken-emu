---
id: plugin.keep-a-session-only-plugin-from-loading
kind: plugin
status: VERIFIED
title: "Keep a session-only plugin from loading"
sources: [S49]
---

# Keep a session-only plugin from loading

**Sources:** [S49](src.s49.md)

To keep a `--plugin-dir` plugin from shadowing anything, or to turn one off when a parent process passes the flag for you, set its id to `false` in any settings file. For a plugin whose manifest name is `hello-plugin`, the entry is `"enabledPlugins": {"hello-plugin@inline": false}`. A disabled session-only plugin doesn't shadow, so the marketplace or skills-directory copy loads instead.
