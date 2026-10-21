---
id: feature.what-changes-when-filesystem-isolation-is-off
kind: feature
status: VERIFIED
title: "What changes when filesystem isolation is off"
sources: [S68]
---

# What changes when filesystem isolation is off

**Sources:** [S68](src.s68.md)

Setting `filesystem.disabled` lifts the protections the filesystem layer itself enforces. Protections that other layers enforce keep applying:
