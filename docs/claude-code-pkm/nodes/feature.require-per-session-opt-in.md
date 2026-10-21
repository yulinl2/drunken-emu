---
id: feature.require-per-session-opt-in
kind: feature
status: VERIFIED
title: "Require per-session opt-in"
sources: [S71]
---

# Require per-session opt-in

**Sources:** [S71](src.s71.md)

By default, fast mode a user turns on in an interactive session persists across sessions. To change this, set `fastModePerSessionOptIn` to `true` in any settings file, which causes each session to start with fast mode off and requires users to explicitly enable it with `/fast`. Owners on Team or Enterprise plans can deploy it organization-wide through server-managed settings.
