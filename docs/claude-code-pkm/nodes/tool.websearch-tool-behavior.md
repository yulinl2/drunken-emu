---
id: tool.websearch-tool-behavior
kind: tool
status: VERIFIED
title: "WebSearch tool behavior"
sources: [S82]
---

# WebSearch tool behavior

**Sources:** [S82](src.s82.md)

WebSearch runs a query against Anthropic's web search backend and returns result titles and URLs. It doesn't fetch the result pages. To read a page Claude finds in search results, it follows up with WebFetch.
