---
id: mcp.failed-discovery-requests
kind: mcp
status: VERIFIED
title: "Failed discovery requests"
sources: [S31]
---

# Failed discovery requests

**Sources:** [S31](src.s31.md)

After a server connects, Claude Code sends it capability discovery requests such as `tools/list`, `prompts/list`, and `resources/list`. Claude Code retries those requests up to three times with short backoff after a transient network or server error. It doesn't retry authentication errors, 4xx responses, or request timeouts.
