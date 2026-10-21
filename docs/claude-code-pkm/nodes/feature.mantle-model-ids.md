---
id: feature.mantle-model-ids
kind: feature
status: VERIFIED
title: "Mantle model IDs"
sources: [S70]
---

# Mantle model IDs

**Sources:** [S70](src.s70.md)

Entries in `availableModels` that start with `anthropic.` are added to the `/model` picker as custom options. This is an exception to the alias matching described in Pin models for third-party deployments. With the Amazon Bedrock Mantle endpoint enabled, Claude Code routes the entries that match the Mantle format to that endpoint. The setting still restricts the picker to listed entries, and a Man
