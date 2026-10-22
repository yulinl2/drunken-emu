---
id: cmd.design-sync
kind: command
status: VERIFIED
title: "/design-sync"
sources: [S80]
---

# /design-sync

**Sources:** [S80](src.s80.md)

Skill. Convert your repo's React design system and upload it to Claude Design, so designs it produces use your real components. Optionally name the design system, for example `/design-sync Acme DS`. A first-time sync verifies every component and can take a few hours on a large repo. Available on the Anthropic API. It needs claude.ai, which the CLI doesn't contact on Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry, or Claude Platform on AWS, or through a Claude apps gateway. The command is unavailable there. This command uploads to the standalone claude.ai/design site, which closes by December 14, 2026; see Migrate from standalone Claude Design to Claude
