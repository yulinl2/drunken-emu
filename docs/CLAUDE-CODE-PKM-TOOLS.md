# Tools inventory

**Snapshot 2026-10-21. Superseded on the same day by the node set.** Back to the [hub](CLAUDE-CODE-PKM.md).

This page holds no prose now. Each tool is one node, `tool.<name>`. These source lists build them:

| Group | Node ids | Source list | Cited source |
|---|---|---|---|
| Official built-in tools, 46 rows (REMOVED rows are marked in their status) | `tool.*` | [06-tools-official.txt](claude-code-pkm/build/src/06-tools-official.txt) | [S6](claude-code-pkm/nodes/src.s6.md) |
| Tools loaded natively in this session | `tool.*` | [07-tools-session.txt](claude-code-pkm/build/src/07-tools-session.txt) | [S7](claude-code-pkm/nodes/src.s7.md), [S8](claude-code-pkm/nodes/src.s8.md) |
| Remote-session, Claude Docs and PDF viewer tools | `tool.remote-*`, `tool.claude-*`, `tool.pdf-*` | [07-tools-session.txt](claude-code-pkm/build/src/07-tools-session.txt) | [S7](claude-code-pkm/nodes/src.s7.md) |
| Connector tools: GitHub 57, Gmail 32 (two are `GAP`), Notion 17, alphaXiv 6 | `tool.github-*`, `tool.gmail-*`, `tool.notion-*`, `tool.alphaxiv-*` | [08-tools-connectors.txt](claude-code-pkm/build/src/08-tools-connectors.txt) | [S7](claude-code-pkm/nodes/src.s7.md); parameters: [gap.connector-schemas](claude-code-pkm/nodes/gap.connector-schemas.md) |

Browse them all in [INDEX: Tools](claude-code-pkm/INDEX.md#tools). The snapshot counts are in [injected.tool-listing-snapshot](claude-code-pkm/nodes/injected.tool-listing-snapshot.md).

The v1 prose is in git: `git show b7bd77f:docs/CLAUDE-CODE-PKM-TOOLS.md`.
