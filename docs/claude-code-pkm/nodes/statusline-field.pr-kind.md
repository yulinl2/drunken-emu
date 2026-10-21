---
id: statusline-field.pr-kind
kind: statusline-field
status: VERIFIED
title: "pr.kind"
sources: [S78]
---

# pr.kind

**Sources:** [S78](src.s78.md)

`mr` when `pr` describes a GitLab merge request. Absent for GitHub pull requests, so scripts written before this field keep working. For a merge request, Claude Code sets `review_state` to `approved` when GitLab reports it mergeable, `pending` for any other open state, and `draft` for a draft. Requires Claude Code v2.1.234 or later
