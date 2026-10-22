---
id: permission-rule.webfetch-permissions-2
kind: permission-rule
status: VERIFIED
title: "WebFetch"
sources: [S66]
---

# WebFetch

**Sources:** [S66](src.s66.md)

WebFetch rules use a `domain:` prefix and match against the hostname of the requested URL. Matching is case-insensitive, supports `*` wildcards, and strips a trailing `.` from both the rule and the hostname so `example.com.` and `example.com` are treated the same.
