---
id: feature.stream-responses
kind: feature
status: VERIFIED
title: "Stream responses"
sources: [S38]
---

# Stream responses

**Sources:** [S38](src.s38.md)

Use `--output-format stream-json` with `--verbose` and `--include-partial-messages` to receive tokens as they're generated. Each line is a JSON object representing an event:
