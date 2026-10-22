---
id: setting-file.global-config
kind: setting-file
status: VERIFIED
title: "Settings file: global config (~/.claude.json)"
sources: [S3]
---

# Settings file: global config (~/.claude.json)

**Sources:** [S3](src.s3.md)

Holds the sign-in session, MCP server configurations, per-project state such as trust decisions, and the global config keys that /config writes. Claude Code writes it; you rarely edit it by hand.

## Linked from

- [CLAUDE_CONFIG_DIR](env.claude-config-dir.md)
