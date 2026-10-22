---
id: env.mcp-sdk-generation
kind: env
status: VERIFIED
title: "MCP_SDK_GENERATION"
sources: [S81]
---

# MCP_SDK_GENERATION

**Sources:** [S81](src.s81.md)

Pin which MCP client runtime this process connects to MCP servers with: `v1`, built on MCP TypeScript SDK 1.x, or `v2`, built on MCP TypeScript SDK 2.0. Without the variable, Claude Code uses v2, starting with the versions listed in that section. On Claude Code v2.1.221 or later, the v2 runtime checks the issuer an MCP OAuth server returns in its authorization response and fails the sign-in with an error that begins `Issuer mismatch in authorization response` when it doesn't match. The v1 runtime doesn't run this check. If you set an unrecognized value, Claude Code ignores it and writes a warning to the debug log. Claude Code reads the value once per process. Requires Claude Code v2.1.218 or later
