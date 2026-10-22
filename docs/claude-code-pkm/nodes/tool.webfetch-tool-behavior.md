---
id: tool.webfetch-tool-behavior
kind: tool
status: VERIFIED
title: "WebFetch tool behavior"
sources: [S82]
---

# WebFetch tool behavior

**Sources:** [S82](src.s82.md)

WebFetch takes a URL and a prompt describing what to extract. It fetches the page and converts the response to Markdown when the server returns HTML. For most fetches, it then runs the prompt against the content in a separate model call, and Claude receives the result of that call rather than the raw page. The conversion step is not configurable.
