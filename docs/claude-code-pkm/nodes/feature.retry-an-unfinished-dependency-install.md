---
id: feature.retry-an-unfinished-dependency-install
kind: feature
status: VERIFIED
title: "Retry an unfinished dependency install"
sources: [S52]
---

# Retry an unfinished dependency install

**Sources:** [S52](src.s52.md)

When the plugin is already at its latest version, the command can also retry an unfinished dependency install in its cached copy. For the cases where that retry runs or is skipped, see The packages it lists are not installed. If the retry fails, the output is `Failed to update plugin "formatter@my-marketplace"` with the reason and the exit code is `1`. Before v2.1.287, the command reported the plu
