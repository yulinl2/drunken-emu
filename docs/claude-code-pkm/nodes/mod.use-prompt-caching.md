---
id: mod.use-prompt-caching
kind: mod
status: VERIFIED
title: "Use prompt caching"
sources: [S56]
---

# Use prompt caching

**Sources:** [S56](src.s56.md)

`$.model.complete` supports the Claude API's prompt caching. The API caches the start of a request, called the prefix, up to a cache breakpoint that you set. When every call starts with the same long static content, such as instructions or reference material, set a breakpoint at the end of that content. Later calls then read it from the cache instead of paying the full input price for it.
