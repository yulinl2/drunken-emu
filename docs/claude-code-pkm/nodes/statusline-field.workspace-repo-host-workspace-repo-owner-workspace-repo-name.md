---
id: statusline-field.workspace-repo-host-workspace-repo-owner-workspace-repo-name
kind: statusline-field
status: VERIFIED
title: "workspace.repo.host, workspace.repo.owner, workspace.repo.name"
sources: [S78]
---

# workspace.repo.host, workspace.repo.owner, workspace.repo.name

**Sources:** [S78](src.s78.md)

Repository identity parsed from the `origin` remote, for example, `"github.com"`, `"anthropics"`, `"claude-code"`. Absent outside a git repository or when no `origin` remote is configured. For a gitlab.com project nested in subgroups, `owner` is the full namespace path with slashes, such as `"group/subgroup"`. Before v2.1.260, `workspace.repo` was absent for these projects
