---
id: feature.message-selector-actions
kind: feature
status: VERIFIED
title: "Message selector actions"
sources: [S79]
---

# Message selector actions

**Sources:** [S79](src.s79.md)

In the message list of the rewind menu, you move through messages and pick one with the Select actions and their default keys. Your `Select` bindings for those actions apply there too. The `MessageSelector` context has no actions or default bindings of its own. Use it to change a key for this list alone, by binding a Select action such as `select:accept` in a `MessageSelector` block.
