---
id: feature.gate-inbound-messages
kind: feature
status: VERIFIED
title: "Gate inbound messages"
sources: [S35]
---

# Gate inbound messages

**Sources:** [S35](src.s35.md)

An ungated channel is a prompt injection vector. Anyone who can reach your endpoint can put text in front of Claude. A channel listening to a chat platform or a public endpoint needs a real sender check before it emits anything.
