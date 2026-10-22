---
id: env.claude-code-plugin-dir-watch
kind: env
status: VERIFIED
title: "CLAUDE_CODE_PLUGIN_DIR_WATCH"
sources: [S81]
---

# CLAUDE_CODE_PLUGIN_DIR_WATCH

**Sources:** [S81](src.s81.md)

Controls whether Claude Code reloads a mod when the mod's files change. Reloading applies to a mod you load from a directory with `--plugin-dir`, and it's on by default in interactive sessions. Set to `1` to turn it on in non-interactive sessions as well, or `0` to turn it off in every session. Requires Claude Code v2.1.287 or later. See mod settings and environment variables
