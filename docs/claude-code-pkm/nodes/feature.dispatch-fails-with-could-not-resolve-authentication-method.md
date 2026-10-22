---
id: feature.dispatch-fails-with-could-not-resolve-authentication-method
kind: feature
status: VERIFIED
title: "Dispatch fails with Could not resolve authentication method"
sources: [S26]
---

# Dispatch fails with Could not resolve authentication method

**Sources:** [S26](src.s26.md)

If a background dispatch fails with `Could not resolve authentication method` while interactive sessions authenticate normally, the worker that received the dispatch didn't pick up credentials. Background sessions get their credentials from the supervisor, so this error means no stored credential was available to the supervisor process itself. Confirm you have run `/login` or configured an API key
