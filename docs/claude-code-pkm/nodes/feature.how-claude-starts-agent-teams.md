---
id: feature.how-claude-starts-agent-teams
kind: feature
status: VERIFIED
title: "How Claude starts agent teams"
sources: [S27]
---

# How Claude starts agent teams

**Sources:** [S27](src.s27.md)

To start a team, ask Claude for teammates. Claude launches a teammate when it calls the Agent tool with a `name` while agent teams are enabled, unless the call is a fork or passes `isolation` on the call itself. Claude Code doesn't ask you to confirm the launch.
