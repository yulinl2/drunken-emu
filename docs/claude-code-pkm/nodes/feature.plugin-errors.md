---
id: feature.plugin-errors
kind: feature
status: VERIFIED
title: "plugin_errors"
sources: [S38]
---

# plugin_errors

**Sources:** [S38](src.s38.md)

plugin load-time errors, each with `plugin`, `type`, and `message`. Includes unsatisfied dependency versions and `--plugin-dir` load failures such as a missing path or invalid archive. A plugin that didn't load is absent from `plugins`. The key is omitted when there are no errors (type: array)
