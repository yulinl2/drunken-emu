---
id: permission-mode.tool-calls-denied-in-claude-p-and-agent-sdk-runs
kind: permission-mode
status: VERIFIED
title: "Tool calls denied in claude -p and Agent SDK runs"
sources: [S67]
---

# Tool calls denied in claude -p and Agent SDK runs

**Sources:** [S67](src.s67.md)

In Claude Code v2.1.302 or later, `claude -p` and Agent SDK runs with no permission mode set start in Manual mode. This mode appears as `default` in SDK options and settings. Calls needing approval are denied unless you approve them with an allow rule, hook, `canUseTool` callback, or `--permission-prompt-tool`.
