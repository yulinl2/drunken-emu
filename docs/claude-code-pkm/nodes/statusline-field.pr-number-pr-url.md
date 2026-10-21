---
id: statusline-field.pr-number-pr-url
kind: statusline-field
status: VERIFIED
title: "pr.number, pr.url"
sources: [S78]
---

# pr.number, pr.url

**Sources:** [S78](src.s78.md)

Open pull request for the current branch. Mirrors the PR badge in the footer. In a repository with a GitLab remote, Claude Code fills these fields from the branch's open merge request instead, so `pr.number` is the merge request number. Merge request data requires Claude Code v2.1.234 or later. Absent when not in a git repository, until a pull request or merge request is found, or once it merges or closes
