---
id: env.disable-doctor-command
kind: env
status: VERIFIED
title: "DISABLE_DOCTOR_COMMAND"
sources: [S81]
---

# DISABLE_DOCTOR_COMMAND

**Sources:** [S81](src.s81.md)

Set to `1` to hide the `/doctor` setup checkup skill and its `/checkup` alias. Useful for managed deployments where users shouldn't run setup diagnostics from a session. Doesn't affect the `claude doctor` terminal command. Before v2.1.205, this variable hid the `/doctor` diagnostics screen command
