---
id: feature.pull-live-data-with-mcp-connectors
kind: feature
status: VERIFIED
title: "Pull live data with MCP connectors"
sources: [S33]
---

# Pull live data with MCP connectors

**Sources:** [S33](src.s33.md)

An artifact can call MCP connectors each time someone views it, so the page shows current data rather than a snapshot from the session that built it. Connector calls from artifacts are available on Pro, Max, Team, and Enterprise plans and require Claude Code v2.1.209 or later. On earlier versions, Claude publishes the page with whatever data the session gathered while building it.
