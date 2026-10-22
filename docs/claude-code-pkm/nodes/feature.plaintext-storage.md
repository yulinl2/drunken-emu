---
id: feature.plaintext-storage
kind: feature
status: VERIFIED
title: "Plaintext storage"
sources: [S16]
---

# Plaintext storage

**Sources:** [S16](src.s16.md)

Transcripts and history are not encrypted at rest. OS file permissions are the only protection. If a tool reads a `.env` file or a command prints a credential, that value is written to `projects//.jsonl`. To reduce exposure:
