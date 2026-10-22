---
id: feature.allow-for-this-session-permission-grants
kind: feature
status: VERIFIED
title: "\"Allow for this session\" permission grants"
sources: [S20]
---

# "Allow for this session" permission grants

**Sources:** [S20](src.s20.md)

after `/branch`: Carried over; the branch runs in the same process, so your existing grants still apply. If you fork into a separate process with `--fork-session`, the new process starts without them and you re-approve there
