---
id: feature.branch-from-a-pull-request
kind: feature
status: VERIFIED
title: "Branch from a pull request"
sources: [S30]
---

# Branch from a pull request

**Sources:** [S30](src.s30.md)

To branch from a specific pull request or merge request, pass `--worktree` the number prefixed with `#`, a GitHub pull request URL, or a GitLab merge request URL such as `https://gitlab.com/group/repo/-/merge_requests/123`. Claude Code fetches that change's head commit from `origin` and creates the worktree at `.claude/worktrees/pr-`. Quote the argument so your shell doesn't treat `#` as the start
