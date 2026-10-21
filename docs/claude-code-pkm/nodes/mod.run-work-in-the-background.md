---
id: mod.run-work-in-the-background
kind: mod
status: VERIFIED
title: "Run work in the background"
sources: [S56]
---

# Run work in the background

**Sources:** [S56](src.s56.md)

Work that outlives one event, such as checking on something once a minute, runs on a timer you start from `session.start`. A hook itself runs for one event and has a time limit on its own execution time. Time spent waiting on `next` or on a mods API call doesn't count, except a `$.clock.sleep`. `$.clock.every` and `$.clock.after` take the place of `setInterval` and `setTimeout`, with the delay in
