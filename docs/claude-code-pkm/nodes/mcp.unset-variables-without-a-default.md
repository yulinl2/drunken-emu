---
id: mcp.unset-variables-without-a-default
kind: mcp
status: VERIFIED
title: "Unset variables without a default"
sources: [S31]
---

# Unset variables without a default

**Sources:** [S31](src.s31.md)

If a referenced environment variable isn't set and has no default value, the config still loads: Claude Code reports a missing-variable warning for that server in `claude mcp list` output and uses the unexpanded `${VAR}` text as-is. Set the variable or add a `:-default` fallback so the server starts with the value you intend. In a remote server's `url` and `headers`, some credential variables read
