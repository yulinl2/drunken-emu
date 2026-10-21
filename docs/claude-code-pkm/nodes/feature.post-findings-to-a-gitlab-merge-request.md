---
id: feature.post-findings-to-a-gitlab-merge-request
kind: feature
status: VERIFIED
title: "Post findings to a GitLab merge request"
sources: [S22]
---

# Post findings to a GitLab merge request

**Sources:** [S22](src.s22.md)

When you pass `--comment` for a GitLab merge request, Claude Code posts the findings through GitLab's `glab` CLI. Requires Claude Code v2.1.257 or later. When `glab` isn't installed, Claude prints the findings in the terminal instead.
