---
id: feature.example-build-a-webhook-receiver
kind: feature
status: VERIFIED
title: "Example: build a webhook receiver"
sources: [S35]
---

# Example: build a webhook receiver

**Sources:** [S35](src.s35.md)

This walkthrough builds a single-file server that listens for HTTP requests and forwards them into your Claude Code session. By the end, anything that can send an HTTP POST, like a CI pipeline, a monitoring alert, or a `curl` command, can push events to Claude.
