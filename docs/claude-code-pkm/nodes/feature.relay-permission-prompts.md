---
id: feature.relay-permission-prompts
kind: feature
status: VERIFIED
title: "Relay permission prompts"
sources: [S35]
---

# Relay permission prompts

**Sources:** [S35](src.s35.md)

When Claude calls a tool that needs approval, the local terminal dialog opens and the session waits. A two-way channel can opt in to receive the same prompt in parallel and relay it to you on another device. Both stay live: you can answer in the terminal or on your phone, and Claude Code applies whichever answer arrives first and closes the other.
