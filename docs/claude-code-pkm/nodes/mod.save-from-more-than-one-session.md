---
id: mod.save-from-more-than-one-session
kind: mod
status: VERIFIED
title: "Save from more than one session"
sources: [S57]
---

# Save from more than one session

**Sources:** [S57](src.s57.md)

Every session on your machine that runs your mod shares one `$.store`. A `get` followed by a `set` isn't atomic. When two sessions each read a value, change it, and write it back, they race, and the second write replaces the first.
