---
id: env.claude-code-debug-logs-dir
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DEBUG_LOGS_DIR"
sources: [S81]
---

# CLAUDE_CODE_DEBUG_LOGS_DIR

**Sources:** [S81](src.s81.md)

Override the debug log file path. Despite the name, this is a file path, not a directory. Requires debug mode to be enabled separately via `--debug`, `/debug`, or the `DEBUG` environment variable: setting this variable alone does not enable logging. The `--debug-file` flag does both at once. Defaults to `~/.claude/debug/.txt`
