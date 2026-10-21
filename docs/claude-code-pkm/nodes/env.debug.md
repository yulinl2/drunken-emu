---
id: env.debug
kind: env
status: VERIFIED
title: "DEBUG"
sources: [S81]
---

# DEBUG

**Sources:** [S81](src.s81.md)

Set to `1` to enable debug mode, equivalent to launching with `--debug`. Debug logs are written to `~/.claude/debug/.txt`, or to the path set by `CLAUDE_CODE_DEBUG_LOGS_DIR`. Only the truthy values `1`, `true`, `yes`, and `on` enable debug mode, so namespace patterns like `DEBUG=express:*` set for other tools do not trigger it
