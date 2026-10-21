---
id: mcp.how-serverurl-entries-match
kind: mcp
status: VERIFIED
title: "How serverUrl entries match"
sources: [S63]
---

# How serverUrl entries match

**Sources:** [S63](src.s63.md)

URLs support `*` wildcards, including `*` as the whole scheme. Hostname matching is case-insensitive and ignores a trailing FQDN dot, so `https://Mcp.Example.com/*` matches `https://mcp.example.com/api`. Paths stay case-sensitive. If you give no port, how you write the hostname decides whether the pattern matches only the scheme's default port or every port:
