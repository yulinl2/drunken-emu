---
id: feature.settings-and-provider
kind: feature
status: VERIFIED
title: "Settings and provider"
sources: [S26]
---

# Settings and provider

**Sources:** [S26](src.s26.md)

A background session reads its settings from the directory it runs in, the same as if you had started `claude` there with the configuration flags it carried over. This includes `env` values in project settings, so an `ANTHROPIC_MODEL` or provider variable set there applies to every background session in that directory.
