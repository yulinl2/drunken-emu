---
id: cli.data-size-plugin
kind: cli
status: VERIFIED
title: "--data-size [plugin]"
sources: [S52]
---

# --data-size [plugin]

**Sources:** [S52](src.s52.md)

Measure each installed plugin's saved data directory, or only the named plugin's, given as `name@marketplace`. Has no effect without `--json`. If the name has no install record, the command prints `--data-size names a plugin that is not installed` and exits `1` instead of printing the list. Requires Claude Code v2.1.285 or later
