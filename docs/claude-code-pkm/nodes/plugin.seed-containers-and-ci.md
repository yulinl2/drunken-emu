---
id: plugin.seed-containers-and-ci
kind: plugin
status: VERIFIED
title: "Seed containers and CI"
sources: [S59]
---

# Seed containers and CI

**Sources:** [S59](src.s59.md)

For container images and CI runners that can't clone at runtime, pre-populate a plugins directory at build time and point `CLAUDE_CODE_PLUGIN_SEED_DIR` at it. Claude Code registers the seed's marketplaces at startup and loads plugin caches from the seed in place, without cloning.
