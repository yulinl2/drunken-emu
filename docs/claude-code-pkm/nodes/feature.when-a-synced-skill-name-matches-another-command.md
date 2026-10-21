---
id: feature.when-a-synced-skill-name-matches-another-command
kind: feature
status: VERIFIED
title: "When a synced skill name matches another command"
sources: [S32]
---

# When a synced skill name matches another command

**Sources:** [S32](src.s32.md)

You can invoke a synced skill by its short name, `/`, or by its full name, `/anthropic-skills:`. When another command uses the short name, `/` runs the other command, and the synced skill runs only as `/anthropic-skills:`. With a local `deploy` skill and a synced `deploy`, `/deploy` runs the local skill and `/anthropic-skills:deploy` runs the synced one. Before v2.1.269, a synced skill had only it
