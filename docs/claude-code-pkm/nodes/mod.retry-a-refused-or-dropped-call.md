---
id: mod.retry-a-refused-or-dropped-call
kind: mod
status: VERIFIED
title: "Retry a refused or dropped call"
sources: [S56]
---

# Retry a refused or dropped call

**Sources:** [S56](src.s56.md)

Make a refused or dropped call again from a `turn.complete` hook. Calls stay refused until the user's next input, and nothing queues or repeats them for you.
