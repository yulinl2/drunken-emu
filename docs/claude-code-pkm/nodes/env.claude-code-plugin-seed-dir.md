---
id: env.claude-code-plugin-seed-dir
kind: env
status: VERIFIED
title: "CLAUDE_CODE_PLUGIN_SEED_DIR"
sources: [S81]
---

# CLAUDE_CODE_PLUGIN_SEED_DIR

**Sources:** [S81](src.s81.md)

Path to one or more read-only plugin seed directories, separated by `:` on Unix or `;` on Windows. Use this to bundle a pre-populated plugins directory into a container image. Claude Code registers marketplaces from these directories at startup and uses pre-cached plugins without re-cloning. See Pre-populate plugins for containers
