---
id: feature.request-id
kind: feature
status: VERIFIED
title: "request_id"
sources: [S35]
---

# request_id

**Sources:** [S35](src.s35.md)

Five lowercase letters drawn from `a`-`z` without `l`, so it never reads as a `1` or `I` when typed on a phone. Include it in your outgoing prompt so it can be echoed in the reply. Claude Code only accepts a verdict that carries an ID it issued. The local terminal dialog doesn't display this ID, so your outbound handler is the only way to learn it.
