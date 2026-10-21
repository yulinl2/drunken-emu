---
id: env.mcp-protocol-negotiation
kind: env
status: VERIFIED
title: "MCP_PROTOCOL_NEGOTIATION"
sources: [S81]
---

# MCP_PROTOCOL_NEGOTIATION

**Sources:** [S81](src.s81.md)

On the v2 MCP client runtime only, whether Claude Code probes servers for MCP protocol revision 2026-07-28. Set `auto` to probe HTTP, claude.ai connector, and stdio servers, or `legacy` to probe none. With the variable unset, Claude Code probes the servers described under MCP client runtimes. Any other value is ignored with a warning in the debug log. Requires Claude Code v2.1.221 or later
