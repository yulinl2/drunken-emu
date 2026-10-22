---
id: feature.connection-and-security
kind: feature
status: VERIFIED
title: "Connection and security"
sources: [S21]
---

# Connection and security

**Sources:** [S21](src.s21.md)

Your local Claude Code session makes outbound HTTPS requests only and never opens inbound ports on your machine. When you start Remote Control, it registers with the Anthropic API and polls for work. When you connect from another device, the server routes messages between the web or mobile client and your local session over a streaming connection.
