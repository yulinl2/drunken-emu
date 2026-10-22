---
id: obs.git-proxy-push-delete-noop
kind: observation
status: REPO
title: "Observation: push --delete was a no-op"
sources: [S9]
---

# Observation: push --delete was a no-op

**Sources:** [S9](src.s9.md)

git push origin --delete through the session's git proxy printed "Everything up-to-date", exited 0 and deleted nothing (SANDBOX-FACTS, 2026-10-18). Deleting a branch is the owner's job, on GitHub.

## Linked from

- [Branch deletion through the git proxy](git-rule.push-delete-noop.md)
