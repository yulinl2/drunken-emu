---
id: cmd.install-github-app
kind: command
status: VERIFIED
title: "/install-github-app"
sources: [S80]
---

# /install-github-app

**Sources:** [S80](src.s80.md)

Install the Claude GitHub App for a repository, with an optional step to set up GitHub Actions workflows and secrets. Walks you through selecting a repo and configuring the integration. Works only with github.com repositories. When your repository's git remote is on gitlab.com or bitbucket.org, the command prints a notice and exits instead of starting setup. To run Claude Code from GitLab pipelines, see GitLab CI/CD
