---
id: permission-rule.when-your-local-settings-file-needs-trust
kind: permission-rule
status: VERIFIED
title: "When your local settings file needs trust"
sources: [S66]
---

# When your local settings file needs trust

**Sources:** [S66](src.s66.md)

`.claude/settings.local.json` is normally your own file, so Claude Code applies its allow rules and additional directories without the trust step. When the file is tracked in git, or `.claude` is a symlink, Claude Code treats it as repository-supplied instead and holds its rules until you trust the folder.
