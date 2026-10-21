# Claude Code tools and harness features: PKM

**Snapshot: 2026-10-21.** Start here. The two inventories are [TOOLS](CLAUDE-CODE-PKM-TOOLS.md), which covers what each tool does and how it is gated, and [HARNESS](CLAUDE-CODE-PKM-HARNESS.md), which covers settings, hooks, memory, skills, subagents, plugins, and background work.

## Start here

| If you need | Go to |
|---|---|
| The official built-in tool table, with permissions | [TOOLS §2](CLAUDE-CODE-PKM-TOOLS.md#2-official-built-in-tools) |
| Every tool loaded in this session, with parameters | [TOOLS §3–§16](CLAUDE-CODE-PKM-TOOLS.md#3-files-and-search) |
| Settings, permissions, hooks, memory, skills, subagents, plugins, MCP | [HARNESS](CLAUDE-CODE-PKM-HARNESS.md) |
| What is unverified, contradicted, or still open | [Open questions](#open-questions) |
| Why the notes are shaped this way | [Decisions](#decisions) |
| Where a tag or claim came from | [Sources](#sources) |

## Counts at a glance

| Count | Value | Tag | Source |
|---|---|---|---|
| Official built-in tools, current (the table has 46 rows; 1 is removed) | 45 | VERIFIED | [S6] |
| Official built-in tools present in this session | 36 of 45 | SESSION | [S6] [S7] [S8] |
| Tools in this session: loaded directly / deferred | 50 / 152 (202 in all) | SESSION | [S7] [S8] |
| Skill entries in this session's listing | 78 | SESSION | [S8] |
| Agent types for the Agent tool | 7 | SESSION | [S8] |
| Hook events | 33 | VERIFIED | [S2] |
| CLI subcommand entries (plus 7 invocation forms) | 29 | VERIFIED | [S4] |
| CLI flags | about 80 | VERIFIED | [S4] |
| English pages in the official docs index | 228 | INDEX | [S1] |

Session counts are my own tallies of the lists in the session context. Recount them during a refresh.

## Legend

| Tag | Meaning |
|---|---|
| `VERIFIED` | Read from an official page fetched on 2026-10-21. |
| `INDEX` | Only the one-line description in the official index. The detail page was not fetched. |
| `SESSION` | Read from this session's live tool schemas or system prompt. These sources have no URL. |
| `REPO` | Observed in this repository's files. Usually one session in one container, so a point, not a settled fact. |
| `UNVERIFIED` | Prior knowledge only. Do not rely on it without a source. |
| `OPEN` | A question, doubt, or conflict. See [Open questions](#open-questions). |

Each claim cites its source in brackets, for example [S6]. Source IDs are defined in [Sources](#sources).

## Glossary

- **Harness**: the runtime around the model: the tool loop, permissions, hooks, memory files, settings, and integrations. [S2] [S3]
- **Built-in tool**: a tool the runtime provides under a fixed name. Permission rules, subagent tool lists, and hook matchers all use that name. [S6]
- **Deferred tool**: a tool whose schema loads only after ToolSearch fetches it. Calling it first fails. [S8]
- **ToolSearch**: the tool that loads deferred schemas, by exact name (`select:`) or by keyword. [S8]
- **Connector**: a claude.ai integration, such as GitHub or Gmail, exposed as tools in this session. [S8]
- **MCP server**: a Model Context Protocol server that adds tools, resources, or prompts. INDEX: [MCP](https://code.claude.com/docs/en/mcp)
- **Hook**: a handler the runtime runs at a named event. Handler types are command, HTTP, MCP tool, prompt, and agent (experimental). [S2]
- **Matcher**: the hook field that selects which tool or source an event applies to. [S2]
- **Skill**: a folder with a `SKILL.md` file (frontmatter plus instructions) that runs as `/name`. [S5]
- **Subagent**: a child agent with its own context window, started by the Agent tool. It returns one final result. [S6]
- **Fork**: a subagent that inherits the full parent conversation. [S6]
- **Teammate**: an agent-team member, started by the Agent tool when agent teams are on. [S6]
- **Permission mode**: the policy that decides when Claude asks before acting. [S4]
- **Permission rule**: a `ToolName(specifier)` entry in an allow, ask, or deny list. [S6]
- **Settings scope**: the file a setting lives in: user, shared project, project local, or managed. [S3]
- **Artifact**: a claude.ai page built from HTML or Markdown. It can be watched, commented on, and given a shared database. [S6] [S7]
- **Remote session**: a session in a cloud environment or on another machine, driven by the claude-code-remote tools. [S7]
- **Background task**: a command or monitor that keeps running after the turn ends. [S6]
- **Workflow**: a rerunnable script that runs many subagents. Opt-in. [S6] [S8]
- **Compaction**: summarizing older context when the window fills. [S2] [S8]
- **Plugin**: a bundle of skills, hooks, MCP servers, agents, and output styles. INDEX: [plugins overview](https://code.claude.com/docs/en/plugins/overview)
- **Mod**: a plugin-style extension that can draw panes, add commands, and react to events. INDEX: [mods overview](https://code.claude.com/docs/en/plugins/mods/overview)

## Sources

| ID | Where | Covers | How checked |
|---|---|---|---|
| S1 | [Docs index](https://code.claude.com/docs/llms.txt) | 228 English pages, with URLs and one-line descriptions | Fetched 2026-10-21 |
| S2 | [Hooks reference](https://code.claude.com/docs/en/hooks) | Events, matchers, stdin and output contracts, exit codes, timeouts, environment variables | Fetched 2026-10-21. The answer covered 100,000 of 269,866 characters, so most per-event stdin schemas are unread |
| S3 | [Settings](https://code.claude.com/docs/en/settings) | Settings files, scopes, precedence, live reload, cloud-session rules, managed exceptions | Fetched 2026-10-21 |
| S4 | [CLI reference](https://code.claude.com/docs/en/cli-reference) | Commands, subcommands, flags, output formats, permission flags | Fetched 2026-10-21 |
| S5 | [Slash commands and skills](https://code.claude.com/docs/en/slash-commands) | Skill files, frontmatter, argument placeholders, namespacing, a partial list of built-in commands | Fetched 2026-10-21. The built-in list is cut off. The full list is on the [Commands](https://code.claude.com/docs/en/commands) page (INDEX), not fetched |
| S6 | [Tools reference](https://code.claude.com/docs/en/tools-reference) | The official tool table (46 rows, with a permission column) and per-tool behavior | Fetched 2026-10-21 and read through line 510 of 708. Lines 511–708 are unread: task availability, Write, WebFetch, WebSearch, large files |
| S7 | Live deferred-tool schemas, this session | Parameters and descriptions of the deferred tools | Loaded with ToolSearch on 2026-10-21. No URL |
| S8 | This session's system prompt and injected context | Directly loaded tools, the skills listing, agent types, and the Git, PR, and output rules | Read on 2026-10-21. No URL |
| S9 | Repository files | Repo conventions and environment observations, each labeled by container class | Read on 2026-10-21: [README](../README.md), [CLAUDE.md](../CLAUDE.md), [OPEN-PROBLEMS](OPEN-PROBLEMS.md), [SANDBOX-FACTS](SANDBOX-FACTS.md), [EXPLORE-SPEC](EXPLORE-SPEC.md), the `.claude/` and `.github/` listings |
| S10 | [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) | Cloud sessions. Named in this session's environment notes | Not fetched |
| S11 | Harness notices, this session | Connection and authorization states of some servers | Read on 2026-10-21. No URL. Server names are not recorded here (Q15) |

## Conflict rule (best of, not union)

When two sources disagree, keep the one closest to the behavior being described. Record the loser as an open question, with both citations. Do not merge the two claims into one row.

Priority order used here:

1. Live schema or official page, for what a tool or setting does: [S2] [S3] [S4] [S6] [S7].
2. This session's system prompt, for rules this session enforces: [S8].
3. Repository observations, labeled by container class: [S9].
4. Prior knowledge, never on its own: `UNVERIFIED`.

## Open questions

Kinds: **Q** question, **D** doubt, **C** concern. Each row names the next check.

| ID | Kind | Item | Evidence | Next check |
|---|---|---|---|---|
| Q1 | Q, conflict | Does a hook added mid-session take effect? | [S3] says edits to hooks apply live, and a settings file created mid-session loads if its folder already existed. [S9]: in one cloud session, a hook added to `.claude/settings.local.json` mid-session produced no evaluation ([OPEN-PROBLEMS](OPEN-PROBLEMS.md) P-dae1, question 3; [SANDBOX-FACTS](SANDBOX-FACTS.md), row of 2026-10-17). A user-level Stop hook did run, and its exit-2 stderr reached the model. The repo's SessionStart banner was also not visible, though [S2] says plain SessionStart stdout is added to context. | Controlled test: one hook present at start, one added mid-session, each logging to a file |
| Q2 | Q, conflict | Why are Glob and Grep loaded here? | [S6]: absent by default on macOS, Linux, and WSL. Naming either in `--tools` or `--allowedTools` restores it. [S8]: both are direct tools in this session. | Find the surface's `--tools` setting. Not visible from inside the session |
| Q3 | Q | Which official tools are missing here? | 36 of 45 are present. Seven of the nine absences match a gate that [S6] describes: EndConversation (cloud sessions excluded), WaitForMcpServers (tool search on), LSP (needs a code-intelligence plugin), PowerShell (opt-in on Linux), TodoWrite (off by default), ShareOnboardingGuide (plan), SubagentHandback (auto mode only). Two are unexplained: RemoteTrigger and SendFeedback. | Read [S6] lines 511–708, then compare with this session's plan and permission mode |
| Q4 | Q | Which models get the Task tools by default? | [S6]: TaskCreate, TaskGet, TaskList, and TaskUpdate are on by default only for a listed set of models. The list sits in the unread lines 511–708. | Read lines 511–708 of the saved tools-reference answer |
| Q5 | D | Are this session's remote scheduling tools the same feature as RemoteTrigger? | [S6] RemoteTrigger creates, updates, runs, and lists cloud scheduled tasks, and backs `/schedule`. [S7] create_trigger and its family do the same job under other names. | Compare input schemas. Decide whether the names are aliases |
| Q6 | D | Which maximum applies to Monitor deadlines? | [S7] schema: `timeout_ms` allows up to 3,600,000 ms. The same schema's description says deadlines above 1,800,000 ms are capped. [S6]: at most 30 minutes. | Treat 30 minutes as the cap, and test one long watch |
| Q7 | Q | What does `--effort ultracode` do beyond xhigh effort? | [S4]: it requests xhigh effort with ultracode turned on (v2.1.203 or later). [S8]: the keyword "ultracode" in a prompt opts into workflows. | Read the workflows anchor that [S4] names |
| Q8 | C | Most harness pages are INDEX-only. | Not fetched: sub-agents, memory, MCP, plugins, interactive mode and keybindings, output styles, status line, checkpointing, permissions, permission modes, sandboxing, headless, env vars, commands, workflows, agent teams, scheduled tasks, remote control. | Next pass, in this order: [commands](https://code.claude.com/docs/en/commands), [interactive mode](https://code.claude.com/docs/en/interactive-mode), [permission modes](https://code.claude.com/docs/en/permission-modes), [sub-agents](https://code.claude.com/docs/en/sub-agents), [memory](https://code.claude.com/docs/en/memory), [env vars](https://code.claude.com/docs/en/env-vars), [workflows](https://code.claude.com/docs/en/workflows) |
| Q9 | C | How far do ListAgents and SendMessage reach? | [S6]: ListAgents lists other local sessions and, with Remote Control connected, cloud sessions and sessions on other machines. [S7]: SendMessage has a `notify_when_idle` flag. | Fetch [cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging) |
| Q10 | C | Model names are kept out of pushed artifacts. | [S8] forbids model identifiers in repo artifacts. Several official pages name model families in examples and digests. These notes paraphrase them ("older models"). | Owner to say whether model aliases are acceptable in docs |
| Q11 | Q | Commit trailer that names a model. | [S8] attribution reminder asks for a named-model trailer. [S8] model-identity rule forbids model identifiers in pushed artifacts. Decision D4 applies. | Owner may redirect |
| Q12 | D | Which container class does a repo observation describe? | [S9] mixes three classes: claude.ai chat (2026-08, "no hook system"), claude.ai project chat (2026-09, `/mnt/project` present), and Claude Code cloud (2026-10, hooks present). Each claim here carries its class. | Sample one container of each class on the same day before generalizing |
| Q13 | Q | Where should human-facing copies go? | [S8]: sustained human-facing materials default to `/mnt/user-data/outputs/`. The git rules designate the repo branch. The outputs folder exists in this session and is empty. | Owner decides whether to mirror a copy there |
| Q14 | C | Connector schemas are listed by name only. | 152 deferred tools; their schemas load on demand. This pass had a budget of 20 tool calls. | Load the GitHub and Gmail families in a later pass if their parameters matter |
| Q15 | C | Connection state is volatile. | [S11] notices name servers that need authorization or failed to connect. Tools from servers that did not load are out of scope for this snapshot. | Re-check at the next session start |

## Decisions

| ID | Decision | Reason | Reverse by |
|---|---|---|---|
| D1 | Put the notes in `docs/` on the designated branch, as three flat files | [S8] designates the branch. The Claude app can open files under the working directory. `docs/` is flat by convention ([OPEN-PROBLEMS](OPEN-PROBLEMS.md) P10 notes this) | Move the files and regenerate `docs/TREE.md` |
| D2 | Three files: this hub, tools, harness | Each file stays readable on its own, and each write is one tool call | Split or merge |
| D3 | Tag each claim with its source type | Official pages change. Session sources have no URL, so the tag is the only way to show where a claim came from | None needed |
| D4 | The commit trailer uses the generic name "Claude" | [S8] forbids model identifiers in pushed artifacts. The reminder's trailer names a model | Owner decision (Q11) |
| D5 | Model names are left out of the notes | [S8] rule (Q10) | Owner decision (Q10) |
| D6 | Connector tools are listed by name only | Call budget. [S8] says their schemas load on demand | Q14 |
| D7 | Pages not fetched are tagged `INDEX`, never `VERIFIED` | The index descriptions are official, but each is one line. Budget | Q8 |
| D8 | Plugin-server connection states are not named | Volatile, and out of scope for loaded tools | None needed |
| D9 | Regenerate `docs/TREE.md` and check it | [README](../README.md) says CI asserts the tracked-file index | None needed |
| D10 | Commit on top of `main` | Before any edit, the designated branch matched `main` and its origin copy. The commit-range checks `main..HEAD` and `HEAD..main` were both empty. [S8] forbids stacking commits on a merged history, and there was none | None needed |

## Not covered in this pass

- [S6] lines 511–708: task availability, Write, WebFetch, WebSearch, and large files.
- The full built-in command list, the keyboard shortcuts, and every INDEX-only page (Q8).
- The 78 skills: names and namespaces only. Their bodies were not read.
- The parameters of the 152 deferred tools, except the families described in [TOOLS](CLAUDE-CODE-PKM-TOOLS.md).

## Refresh procedure

1. Fetch the [docs index](https://code.claude.com/docs/llms.txt). Diff its page list against the links in these files.
2. Load the deferred schemas with ToolSearch, using `select:` and the names in TOOLS §3–§16. Recount.
3. Re-fetch [S6], [S3], [S4], and [S2], then the Q8 pages in order. Change only the rows whose source changed, and record the date.
4. From the repo root, run `python3 bin/gen_tree.py --write`, then `python3 bin/gen_tree.py --check`.

[S1]: https://code.claude.com/docs/llms.txt
[S2]: https://code.claude.com/docs/en/hooks
[S3]: https://code.claude.com/docs/en/settings
[S4]: https://code.claude.com/docs/en/cli-reference
[S5]: https://code.claude.com/docs/en/slash-commands
[S6]: https://code.claude.com/docs/en/tools-reference
[S7]: #sources
[S8]: #sources
[S9]: #sources
[S10]: https://code.claude.com/docs/en/claude-code-on-the-web
[S11]: #sources
