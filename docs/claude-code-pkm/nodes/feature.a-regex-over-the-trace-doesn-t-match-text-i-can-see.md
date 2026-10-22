---
id: feature.a-regex-over-the-trace-doesn-t-match-text-i-can-see
kind: feature
status: VERIFIED
title: "A regex over the trace doesn't match text I can see"
sources: [S47]
---

# A regex over the trace doesn't match text I can see

**Sources:** [S47](src.s47.md)

Wrong target: the default `target` is `last_message`, not the trace. JSON escaping: when you do target `trace`, it's JSON per line, so quotes appear as `\"`. Regex syntax: regexes use JavaScript syntax, so put `i` in `flags` rather than writing `(?i)`.
