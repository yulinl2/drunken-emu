---
id: cli.json-plugins-cli-reference-6
kind: cli
status: VERIFIED
title: "--json"
sources: [S52]
---

# --json

**Sources:** [S52](src.s52.md)

Print the result as one JSON object on stdout. Without `--values-stdin`, the object carries the options' `schema` and `choices`, their starting `inputs`, and the `configured` and `unconfigured` option names. With `--values-stdin`, it carries the `saved` option names and, when they could be read back, the `unconfigured` ones
