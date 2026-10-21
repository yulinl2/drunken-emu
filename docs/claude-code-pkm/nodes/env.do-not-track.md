---
id: env.do-not-track
kind: env
status: VERIFIED
title: "DO_NOT_TRACK"
sources: [S81]
---

# DO_NOT_TRACK

**Sources:** [S81](src.s81.md)

Set to `1` to opt out of telemetry, with the same effect as `DISABLE_TELEMETRY`, including on feature-flag fetching. Claude Code reads this variable as a standard boolean, so `0` leaves telemetry on, and honors it as the cross-tool convention recognized by many developer CLIs
