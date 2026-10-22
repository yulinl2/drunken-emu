---
id: feature.mock-call-budget-exceeded
kind: feature
status: VERIFIED
title: "\"mock call budget exceeded\""
sources: [S47]
---

# "mock call budget exceeded"

**Sources:** [S47](src.s47.md)

Every `type: agent` mock in a run draws on one call budget of four times the case's `max_turns`, which is 40 calls at the default of 10. Calls answered from `.replay/` recordings count too, and the case's `mock budget` progress line prints the budget. A call past it aborts the run with score 0 and this reason, so raise `max_turns` in the case for a skill that makes many calls to agent mocks.
