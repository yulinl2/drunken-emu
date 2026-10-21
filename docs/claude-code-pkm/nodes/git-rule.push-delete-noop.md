---
id: git-rule.push-delete-noop
kind: git-rule
status: REPO
title: "Branch deletion through the git proxy"
sources: [S9]
---

# Branch deletion through the git proxy

**Sources:** [S9](src.s9.md)

Observed: git push --delete through the session's proxy printed "Everything up-to-date" and deleted nothing ([Observation: push --delete was a no-op](obs.git-proxy-push-delete-noop.md)).
