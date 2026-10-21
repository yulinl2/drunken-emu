---
id: feature.turn-off-permission-prompts-in-unattended-runs
kind: feature
status: VERIFIED
title: "Turn off permission prompts in unattended runs"
sources: [S38]
---

# Turn off permission prompts in unattended runs

**Sources:** [S38](src.s38.md)

Pass `--permission-prompts none` when nobody is available to answer permission prompts, for example in a scheduled job. The flag matters most when your run has a permission host: an Agent SDK app with a `canUseTool` callback, or an MCP tool you pass with `--permission-prompt-tool`. Without the flag, your run waits for that host to answer each permission request.
