---
id: feature.case-yaml-fields
kind: feature
status: VERIFIED
title: "case.yaml fields"
sources: [S47]
---

# case.yaml fields

**Sources:** [S47](src.s47.md)

`case.yaml` is an alternative or companion to `prompt.md`: it describes a case in YAML and adds the fields that point at other files. It requires `schema_version: "1.1"` and `name`. The `prompt.md` fields `description`, `tags`, `plugins`, `runs`, and `expected_outcome` go at the top level; `model`, `max_turns`, `timeout_seconds`, `allowed_tools`, `append_system_prompt`, and `env` go under `executi
