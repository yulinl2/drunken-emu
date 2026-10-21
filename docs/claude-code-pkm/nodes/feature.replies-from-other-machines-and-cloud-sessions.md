---
id: feature.replies-from-other-machines-and-cloud-sessions
kind: feature
status: VERIFIED
title: "Replies from other machines and cloud sessions"
sources: [S28]
---

# Replies from other machines and cloud sessions

**Sources:** [S28](src.s28.md)

A cloud session, including one on a self-hosted runner, can't use `SendMessage` to answer a message from another machine, even when the message carries a reply address. The message still arrives. Read the cloud session's response in its transcript at claude.ai/code.
