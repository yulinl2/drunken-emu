---
id: mcp.tool-input-schemas-with-a-root-level-combinator
kind: mcp
status: VERIFIED
title: "Tool input schemas with a root-level combinator"
sources: [S31]
---

# Tool input schemas with a root-level combinator

**Sources:** [S31](src.s31.md)

Some MCP servers declare a tool's input schema as a JSON Schema union, with `anyOf`, `oneOf`, or `allOf` at the top level of the schema. The Claude API doesn't accept those keywords at the schema root. It does accept combinators nested inside `properties`, which Claude Code sends unchanged.
