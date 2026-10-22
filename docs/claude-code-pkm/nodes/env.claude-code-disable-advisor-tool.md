---
id: env.claude-code-disable-advisor-tool
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_ADVISOR_TOOL"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_ADVISOR_TOOL

**Sources:** [S81](src.s81.md)

Set to `1` to disable the advisor tool. The `/advisor` command becomes unavailable, any configured `advisorModel` is ignored, and the `--advisor` flag is accepted but has no effect, so existing scripts that pass it continue to work without errors
