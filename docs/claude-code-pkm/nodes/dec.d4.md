---
id: dec.d4
kind: decision
status: DECIDED
title: "D4: Commit trailer uses the generic name Claude"
sources: [S8]
---

# D4: Commit trailer uses the generic name Claude

**Sources:** [S8](src.s8.md)

The session forbids model identifiers in pushed artifacts ([S8: This session's system prompt and injected context](src.s8.md)), and the attribution reminder's trailer names a model. The commit trailer therefore reads Co-Authored-By: Claude with a generic address. The Claude-Session trailer is kept. Owner decision: [Q11: Commit trailer that names a model.](question.q11.md).

## Linked from

- [Attribution in commits and PRs](git-rule.attribution.md)
- [D5: Model names are left out of the notes](dec.d5.md)
- [Q11: Commit trailer that names a model.](question.q11.md)
