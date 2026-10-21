---
id: feature.embed-a-link-in-a-runbook
kind: feature
status: VERIFIED
title: "Embed a link in a runbook"
sources: [S39]
---

# Embed a link in a runbook

**Sources:** [S39](src.s39.md)

A deep link in a runbook gives whoever is triaging a one-click way to start investigating in the right repository with a prepared prompt. The platform that renders the runbook must allow custom URL schemes. GitHub-rendered Markdown does not allow `claude-cli://`, so a deep link in a GitHub README, issue, or wiki shows only its label with no clickable link. See the troubleshooting note for a workar
