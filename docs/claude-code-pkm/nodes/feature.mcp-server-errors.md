---
id: feature.mcp-server-errors
kind: feature
status: VERIFIED
title: "mcp_server_errors"
sources: [S38]
---

# mcp_server_errors

**Sources:** [S38](src.s38.md)

`--mcp-config` entries skipped by config validation, each with `name`, `type`, and `message`. `type` is a skip category such as `unknown_type`, `url_missing_type`, `invalid_config`, or `reserved_name`; treat values you don't recognize as a generic skip. Affected servers are absent from `mcp_servers`. The key is omitted when there are no errors, so a CI gate can fail on a non-empty array. Requires Claude Code v2.1.219 or later (type: array)
