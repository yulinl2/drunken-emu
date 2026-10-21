---
id: mod.the-order-mods-run-in
kind: mod
status: VERIFIED
title: "The order mods run in"
sources: [S55]
---

# The order mods run in

**Sources:** [S55](src.s55.md)

Hooks on the same event form one middleware chain. Each mod's `next` calls the following mod's hook, and the last `next` reaches Claude Code's own behavior. The first mod is outermost: it sees the event before the others and the result after them, and it decides whether the others run at all. A later mod can't stop an earlier one from seeing an event.
