---
id: mcp.add-a-server-from-an-npx-uvx-or-binary-command
kind: mcp
status: VERIFIED
title: "Add a server from an npx, uvx, or binary command"
sources: [S31]
---

# Add a server from an npx, uvx, or binary command

**Sources:** [S31](src.s31.md)

A launch command means the server runs as a local stdio process. Put the whole command after `--`, so Claude Code passes flags such as `-y` to the command that starts the server instead of reading them as its own options. Pass any environment variables the instructions ask for with `--env`, after the server name and before `--`:
