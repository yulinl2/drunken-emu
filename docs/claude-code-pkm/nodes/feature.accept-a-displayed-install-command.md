---
id: feature.accept-a-displayed-install-command
kind: feature
status: VERIFIED
title: "Accept a displayed install command"
sources: [S52]
---

# Accept a displayed install command

**Sources:** [S52](src.s52.md)

When a `--json` run displays a marketplace-declared command and doesn't run it, the `failed` result also carries a `shownCommand` object. Its fields include the command as displayed, the plugin it belongs to, and the command's `sha256`.
