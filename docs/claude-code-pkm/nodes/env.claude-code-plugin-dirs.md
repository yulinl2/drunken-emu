---
id: env.claude-code-plugin-dirs
kind: env
status: VERIFIED
title: "CLAUDE_CODE_PLUGIN_DIRS"
sources: [S81]
---

# CLAUDE_CODE_PLUGIN_DIRS

**Sources:** [S81](src.s81.md)

Plugin directories to load for the session, each loaded the way a `--plugin-dir` flag loads it. Separate multiple paths with `:` on Unix or `;` on Windows. Give each path as an absolute path or start it with `~`, because Claude Code skips relative paths. Requires Claude Code v2.1.280 or later. See Load a plugin for one session
