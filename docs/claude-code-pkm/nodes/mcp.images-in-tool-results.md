---
id: mcp.images-in-tool-results
kind: mcp
status: VERIFIED
title: "Images in tool results"
sources: [S31]
---

# Images in tool results

**Sources:** [S31](src.s31.md)

When an MCP tool returns a PNG, JPEG, GIF, or WebP image, Claude sees the image inline in the conversation. The inline copy may be scaled down or compressed to fit the model's image size limits. Claude Code also saves the original bytes to a file in the session's `tool-results` directory under `~/.claude/projects/` and gives Claude the path. Claude can then crop, convert, or reuse the full-resolut
