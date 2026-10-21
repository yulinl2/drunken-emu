---
id: tool.large-files
kind: tool
status: VERIFIED
title: "Large files"
sources: [S82]
---

# Large files

**Sources:** [S82](src.s82.md)

Claude can read a text file larger than a single Read call returns. By default one call returns at most 25,000 tokens, or the value you set in `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS`, and refuses a whole file over 256 KB, so Claude reads a larger file in pages with `offset` and `limit`. On Claude Code v2.1.296 or later it can instead read the whole file, or a long line range, in one call by sett
