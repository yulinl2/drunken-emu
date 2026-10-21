---
id: env.claude-code-plugin-cache-dir
kind: env
status: VERIFIED
title: "CLAUDE_CODE_PLUGIN_CACHE_DIR"
sources: [S81]
---

# CLAUDE_CODE_PLUGIN_CACHE_DIR

**Sources:** [S81](src.s81.md)

Override the plugins root directory. Despite the name, this sets the parent directory, not the cache itself: marketplaces and the plugin cache live in subdirectories under this path. Defaults to `~/.claude/plugins`
