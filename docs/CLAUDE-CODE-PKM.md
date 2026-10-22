# Claude Code tools and harness features: PKM

**Snapshot: 2026-10-21.** Start here. The notes are one node per concept, under [`claude-code-pkm/`](claude-code-pkm/INDEX.md). Each node is generated from the source lists in [`build/src/`](claude-code-pkm/build/src/), so edit the lists and rebuild. Do not edit the nodes.

## Where things are

| Path | What it holds |
|---|---|
| [INDEX.md](claude-code-pkm/INDEX.md) | Every node, grouped by kind, with its tag and a one-line summary. The node count and the count by kind are at the top. |
| [nodes/](claude-code-pkm/nodes/) | One page per concept: frontmatter, sources, body, and a "Linked from" list. |
| [build/src/](claude-code-pkm/build/src/) | The source lists, one file per area. This is the only place to edit content. |
| [build/build_nodes.py](claude-code-pkm/build/build_nodes.py) | The generator. It checks every row, id, source and link, then writes the nodes and the index. If a check fails, it writes nothing. |

## Start here

| If you need | Go to |
|---|---|
| The official tool table, and the tools loaded in this session | [Tools](claude-code-pkm/INDEX.md#tools) |
| Hook events, matchers, exit codes and timeouts | [Hook events](claude-code-pkm/INDEX.md#hook-events), [Hook rules](claude-code-pkm/INDEX.md#hook-rules) |
| Settings, precedence, permission modes and rules, memory | [Settings](claude-code-pkm/INDEX.md#settings), [Precedence](claude-code-pkm/INDEX.md#precedence), [Permission modes](claude-code-pkm/INDEX.md#permission-modes), [Permission rules](claude-code-pkm/INDEX.md#permission-rules), [Memory](claude-code-pkm/INDEX.md#memory) |
| Skills, slash commands, CLI subcommands and flags | [Skills](claude-code-pkm/INDEX.md#skills), [Slash commands](claude-code-pkm/INDEX.md#slash-commands), [CLI subcommands](claude-code-pkm/INDEX.md#cli-subcommands), [CLI flags](claude-code-pkm/INDEX.md#cli-flags) |
| Plugins, mods, MCP, features and agent types | [Plugins](claude-code-pkm/INDEX.md#plugins), [Mods](claude-code-pkm/INDEX.md#mods), [MCP](claude-code-pkm/INDEX.md#mcp), [Features](claude-code-pkm/INDEX.md#features), [Agent types](claude-code-pkm/INDEX.md#agent-types) |
| Environment, processes, git and PR rules, injected context | [Environment variables](claude-code-pkm/INDEX.md#environment-variables), [Processes](claude-code-pkm/INDEX.md#processes), [Git and PR rules](claude-code-pkm/INDEX.md#git-and-pr-rules), [Injected context](claude-code-pkm/INDEX.md#injected-context) |
| Glossary, tags and sources | [Glossary](claude-code-pkm/INDEX.md#glossary), [Legend tags](claude-code-pkm/INDEX.md#legend-tags), [Sources](claude-code-pkm/INDEX.md#sources) |
| What is unverified, contradicted or still open | [Open questions](claude-code-pkm/INDEX.md#open-questions), [Coverage gaps](claude-code-pkm/INDEX.md#coverage-gaps) |
| Why the notes are shaped this way | [Decisions](claude-code-pkm/INDEX.md#decisions) |

## Scope and done

- **Scope (dec.d12, decided).** The PKM covers Claude Code as a harness: tools, commands, flags, settings, environment variables, hooks, memory, skills, subagents, plugins and mods, MCP, permissions, sandboxing, output styles, status line and keyboard shortcuts. The 72 in-scope reference pages are listed in `build/extract_pages.py`, and each has its own source node. See [dec.d12](claude-code-pkm/nodes/dec.d12.md).
- **Out of scope (dec.d14).** The other 152 English pages on the docs index are listed with a reason each, grouped by reason. See [dec.d14](claude-code-pkm/nodes/dec.d14.md).
- **Done (dec.d13).** No GAP-status node remains. Every table row and section heading on an in-scope page is a node or is already present. The English index pages split exactly into in-scope and out-of-scope, and both drift checks pass. See [dec.d13](claude-code-pkm/nodes/dec.d13.md).
- **Regenerate.** Download the in-scope pages as described in `build/src/19-pages-tables.txt`, run `build/extract_pages.py`, run `build/best_of.py`, then run `build/build_nodes.py`.

## Method

- **Tags.** Each node's `status` is one tag: `VERIFIED`, `INDEX`, `SESSION`, `REPO`, `UNVERIFIED`, `OPEN`, `GAP`, `DECIDED`, `SUPERSEDED`, `REMOVED` or `DEFINED`. Their meanings are in [Legend tags](claude-code-pkm/INDEX.md#legend-tags).
- **Sources.** Each node cites its sources as `S<n>`, and each citation links to a source node. The list is in [Sources](claude-code-pkm/INDEX.md#sources).
- **Conflicts.** Keep the source closest to the behavior, and record the loser as an open question. See [process.conflict-rule](claude-code-pkm/nodes/process.conflict-rule.md).
- **Overlaps.** Nodes that describe the same thing on the same surface form one group. The winner is chosen by a stated order, and each loser is demoted to SUPERSEDED with its text kept behind a pointer. Nothing is merged. See [dec.d15](claude-code-pkm/nodes/dec.d15.md).

## Refresh

1. Fetch the [docs index](https://code.claude.com/docs/llms.txt) and diff its page list against the source lists.
2. Download the in-scope pages again, then rerun `build/extract_pages.py`. A generated row keeps its text when a hand-written node has the same id, so change that node by hand.
3. Load the deferred schemas with ToolSearch, using `select:`, and resolve [gap.connector-schemas](claude-code-pkm/nodes/gap.connector-schemas.md).
4. Edit `build/src/*.txt`, then run `python3 docs/claude-code-pkm/build/build_nodes.py`, then `python3 docs/claude-code-pkm/build/build_nodes.py --check`.
5. From the repo root, run `python3 bin/gen_tree.py --write`, then `python3 bin/gen_tree.py --check`.

The build steps are also in [process.build](claude-code-pkm/nodes/process.build.md).

## What changed on 2026-10-21

The v1 prose was factorized into nodes, as decided in [dec.d11](claude-code-pkm/nodes/dec.d11.md). The v1 text stays in git history, not in the working tree:

- The v1 hub: `git show b7bd77f:docs/CLAUDE-CODE-PKM.md`. The tools and harness pages: `git show b7bd77f:docs/CLAUDE-CODE-PKM-TOOLS.md` and `git show b7bd77f:docs/CLAUDE-CODE-PKM-HARNESS.md`.
- [TOOLS](CLAUDE-CODE-PKM-TOOLS.md) and [HARNESS](CLAUDE-CODE-PKM-HARNESS.md) are now pointer pages.
- Replaced decisions stay as nodes with status `SUPERSEDED`: [dec.d2](claude-code-pkm/nodes/dec.d2.md) and [dec.d6](claude-code-pkm/nodes/dec.d6.md). Nothing is deleted from the node set.
