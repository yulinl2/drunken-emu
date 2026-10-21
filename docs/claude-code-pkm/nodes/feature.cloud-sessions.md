---
id: feature.cloud-sessions
kind: feature
status: VERIFIED
title: "Cloud sessions"
sources: [S69]
---

# Cloud sessions

**Sources:** [S69](src.s69.md)

A cloud session runs in an isolated, Anthropic-managed virtual machine. A network proxy enforces a default allowlist, and a separate proxy holds your GitHub token outside the sandbox while issuing scoped credentials for repository access inside it. Sessions your organization routes to a self-hosted environment run on infrastructure you provision instead, where isolation, egress control, and git cr
