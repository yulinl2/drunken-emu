---
id: feature.tools-are-denied-mcp-tools-are-missing-or-bash-won-t-run
kind: feature
status: VERIFIED
title: "Tools are denied, MCP tools are missing, or Bash won't run"
sources: [S47]
---

# Tools are denied, MCP tools are missing, or Bash won't run

**Sources:** [S47](src.s47.md)

Anything beyond the read-only set needs your grant, such as `--allow-tools Bash Write`. Your personal MCP servers never load in a run. The plugin's own servers don't start unless you opt in, and their tools then also need an `--allow-tools "mcpplugin*"` grant; a mocked tool needs neither.
