---
id: feature.allowlist-the-viewer-domain
kind: feature
status: VERIFIED
title: "Allowlist the viewer domain"
sources: [S33]
---

# Allowlist the viewer domain

**Sources:** [S33](src.s33.md)

The viewer on claude.ai loads each artifact from a sandboxed `*.claudeusercontent.com` origin. If your organization restricts outbound network access, add that domain to your allowlist alongside `claude.ai`. See Network access requirements for the full list.
