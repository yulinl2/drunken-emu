# Tools inventory

**Snapshot 2026-10-21.** Back to the [hub](CLAUDE-CODE-PKM.md). Tags and source IDs are defined there.

## 1. How tools reach a session

- **Direct**: the full schema is in the session's tool list from the start. [S8]
- **Deferred**: only the name is listed. ToolSearch loads the schema. Use `select:<name>` for exact names, or keywords. The default `max_results` is 5. [S8]
- **Permission column** (from [S6]): "Yes" means the tool asks for approval in Manual mode for paths inside the working directory. File-access tools marked "No" still prompt for paths outside it. Bash runs a built-in set of read-only commands without asking.

## 2. Official built-in tools

Source: [S6], 46 rows. "Here" is this session's status. Descriptions are condensed from [S6].

| Tool | Permission | Here | What it does |
|---|---|---|---|
| `Agent` | No | direct | Spawns a subagent with its own context window. With agent teams on, a call with a `name` launches a teammate |
| `Artifact` | Yes | direct | Publishes an HTML or Markdown page to claude.ai. Needs a Pro, Max, Team, or Enterprise plan and `/login` |
| `AskUserQuestion` | No | direct | Asks multiple-choice questions. Questions stay open until answered, unless `askUserQuestionTimeout` is set |
| `Bash` | Yes | direct | Runs shell commands |
| `CronCreate` | No | deferred | Schedules a recurring or one-shot prompt in this session |
| `CronDelete` | No | deferred | Cancels a session-scoped scheduled task |
| `CronList` | No | deferred | Lists session-scoped scheduled tasks |
| `Edit` | Yes | direct | Exact string replacement in a file |
| `EndConversation` | No | absent | Ends a session in rare cases of sustained abuse, or when asked to demonstrate. Not offered in cloud sessions, the SDK, `-p` runs, or `--bare` |
| `EnterPlanMode` | No | deferred | Switches to plan mode |
| `EnterWorktree` | Yes | deferred | Creates or enters a git worktree. Paths outside `.claude/worktrees/` need approval |
| `ExitPlanMode` | Yes | deferred | Presents a plan for approval and exits plan mode |
| `ExitWorktree` | No | deferred | Leaves a worktree session |
| `Glob` | No | direct | Finds files by pattern. Absent by default on macOS, Linux, and WSL (Q2) |
| `Grep` | No | direct | Searches file contents. Absent by default on macOS, Linux, and WSL (Q2) |
| `ListAgents` | No | direct | Lists the agents that `SendMessage` can reach |
| `ListMcpResourcesTool` | No | deferred | Lists resources from connected MCP servers, leaving out MCP Apps UI resources |
| `LSP` | No | absent | Language-server navigation and type errors. Needs a code-intelligence plugin. Not started in cloud sessions |
| `Monitor` | Yes | deferred | Runs a command in the background and feeds each output line back, or opens a WebSocket |
| `NotebookEdit` | Yes | deferred | Edits Jupyter cells by `cell_id` |
| `PowerShell` | Yes | absent | PowerShell commands. Default on Windows, opt-in on Linux, macOS, and WSL |
| `PushNotification` | No | deferred | Desktop notification, plus phone push when Remote Control is connected |
| `Read` | No | direct | Reads files, images, PDFs, and notebooks |
| `ReadMcpResourceTool` | No | deferred | Reads one MCP resource by URI |
| `RemoteTrigger` | No | absent | Creates, updates, runs, and lists cloud scheduled tasks, and backs `/schedule`. Not present here (Q3, Q5) |
| `ReportFindings` | No | direct | Reports code-review findings as a structured list |
| `ScheduleWakeup` | No | direct | Sets the next `/loop` iteration, between 1 minute and 1 hour out. `stop: true` ends the loop |
| `SendFeedback` | No | absent | Drafts a feedback report for review. Sends nothing until approved. Not present here (Q3) |
| `SendMessage` | No | deferred | Messages a teammate, a resumed subagent, or another session |
| `SendUserFile` | No | direct | Sends a file to the user, rendered inline or as a download |
| `ShareOnboardingGuide` | Yes | absent | Uploads `ONBOARDING.md` for teammates. Team and Enterprise plans |
| `Skill` | Yes | direct | Runs a skill inside the main conversation |
| `SubagentHandback` | No | absent | Delivers a subagent's final report. Auto mode only |
| `TaskCreate` | No | deferred | Creates a task. On by default only for listed models, and opt-in elsewhere (Q4) |
| `TaskGet` | No | deferred | Reads one task |
| `TaskList` | No | deferred | Lists tasks |
| `TaskOutput` | No | removed | Removed in v2.1.277. Read a background task's output file with `Read` |
| `TaskStop` | No | deferred | Stops a background task, a teammate, or a named agent |
| `TaskUpdate` | No | deferred | Updates status, dependencies, and details, or deletes a task |
| `TodoWrite` | No | absent | Checklist tool. Disabled by default in favor of the Task tools |
| `ToolSearch` | No | direct | Loads deferred tool schemas |
| `WaitForMcpServers` | No | absent | Waits for MCP servers that are still connecting. Appears only when tool search is off |
| `WebFetch` | Yes | deferred | Fetches a URL |
| `WebSearch` | Yes | deferred | Web search |
| `Workflow` | Yes | direct | Runs a dynamic workflow that orchestrates many subagents |
| `Write` | Yes | direct | Creates or overwrites files |

**Summary.** 36 of the 45 current tools are present here, and 9 are absent. Seven of the nine absences match a gate that [S6] describes. `RemoteTrigger` and `SendFeedback` are unexplained (Q3). Fifteen native tools in this session are not in the official table, and the remote, docs, connector, and plugin families are session-specific as well.

## 3. Files and search

### Direct (SESSION, [S8])

| Tool | Parameters | Notes |
|---|---|---|
| `Read` | `file_path` (absolute), `offset`, `limit`, `pages`, `allow_large` | 2,000 lines by default. Handles images, PDFs (ranges of up to 20 pages), and notebooks. [S6] |
| `Write` | `file_path`, `content` | Overwrites. Read an existing file first. [S8] |
| `Edit` | `file_path`, `old_string`, `new_string`, `replace_all` | Exact match, and unique unless `replace_all` is set. Some older models always need a prior Read. [S6] |
| `Glob` | `pattern`, `path` | Sorted by modification time. Capped at 100 files. Ignores `.gitignore` by default. [S6] |
| `Grep` | `pattern`, `path`, `glob`, `type`, `output_mode`, `-A`, `-B`, `-C`, `-i`, `-n`, `head_limit`, `offset`, `multiline` | ripgrep regex syntax. Skips gitignored files. Modes: files_with_matches (default), content, count. [S6] [S8] |

### Deferred (SESSION, [S7])

| Tool | Parameters | Notes |
|---|---|---|
| `NotebookEdit` | `notebook_path`, `new_source`, `cell_id`, `cell_type` (code or markdown), `edit_mode` (replace, insert, delete) | UTF-8 only. Permission rules use the `Edit(...)` path form. [S6] |

## 4. Shell and background

| Tool | Permission | Here | Parameters | Notes |
|---|---|---|---|---|
| `Bash` | Yes | direct | `command`, `description`, `timeout`, `run_in_background`, `dangerouslyDisableSandbox` | Each command runs in its own process. Default timeout 2 min. Foreground ceiling 10 min (`BASH_DEFAULT_TIMEOUT_MS`, `BASH_MAX_TIMEOUT_MS`). Background default 30 min, cap 2 h, enforced only in unattended runs. Valid output is inline up to about 30,000 characters, and failed output up to about 10,000. [S6] [S8] |
| `Monitor` | Yes | deferred | `command` or `ws` (`url`, `protocols`), `description`, `timeout_ms` | Deadline 5 min by default, 30 min at most, 10 min under `-p`. Refuses private and metadata addresses. Not on Bedrock, Agent Platform, or Foundry. [S6] [S7] (Q6) |
| `TaskStop` | No | deferred | `task_id` (`shell_id` is deprecated) | Stops a background task. [S6] [S7] |
| `PowerShell` | Yes | absent | none in this session | Windows default, opt-in elsewhere. [S6] |

Notes:

- `cd` persists within the project, but environment variables do not. `CLAUDE_ENV_FILE` makes them persist. [S6]
- `/tasks` lists and stops background tasks. [S6]
- `$CLAUDE_PROJECT_DIR` was unset in this Bash tool's environment (2026-10-17). [SANDBOX-FACTS](SANDBOX-FACTS.md), [S9]

## 5. Web

| Tool | Permission | Here | Parameters | Notes |
|---|---|---|---|---|
| `WebFetch` | Yes | deferred | `url`, `prompt`, `offset` | 15-minute cache. Refuses authenticated URLs. Artifact links go through the Artifact tool. Cross-host redirects come back to the caller. [S6] [S7] |
| `WebSearch` | Yes | deferred | `query` (2+ characters), `mode` (standard or extended), `allowed_domains`, `blocked_domains` | Use standard for routine lookups. Extended costs several times more. Ends with a Sources list. [S6] [S7] |

Rule forms: `WebFetch(domain:example.com)`, and a bare `WebSearch`. [S6]

## 6. Agents and orchestration

| Tool | Permission | Here | Parameters | Notes |
|---|---|---|---|---|
| `Agent` | No | direct | `description`, `prompt`, `subagent_type` (`fork` or a named type), `isolation` (`worktree` or `remote`), `run_in_background`, `model` (an alias enum; values not reproduced here) | Subagents run in the background by default. Foreground subagents show permission prompts in place. Background ones send prompts to the main session. Limits come from `tools`, `disallowedTools`, and `maxTurns`. [S6] [S7] [S8] |
| `SendMessage` | No | deferred | `to`, `message`, `summary` (5 to 10 words, cut at 200 characters), `notify_when_idle` (main conversation only) | Reaches teammates, resumed subagents, and other sessions. [S6] [S7] |
| `ListAgents` | No | direct | `channel` and `q` are listed but unavailable in this build | Lists messageable agents. Appears only when cross-session messaging is on. [S6] [S8] |
| `Workflow` | Yes | direct | `script`, or `scriptPath`, or `name`; `args`; `resumeFromRunId` | Opt-in only. Default guideline: under 10 agents. Watch progress with `/workflows`. Returns one consolidated result. [S6] [S7] [S8] |
| `TaskCreate` | No | deferred | `subject`, `description`, `activeForm`, `metadata` | Availability depends on the model (Q4). [S6] [S7] |
| `TaskGet` | No | deferred | `taskId` | Availability as above. |
| `TaskList` | No | deferred | none | Availability as above. |
| `TaskUpdate` | No | deferred | `taskId`, `status` (pending, in_progress, completed, deleted), `subject`, `description`, `activeForm`, `owner`, `metadata`, `addBlocks`, `addBlockedBy` | Availability as above. [S7] |

Agent types in this session [S8]:

- `claude`: the catch-all type.
- `claude-code-guide`: questions about Claude Code, the Agent SDK, the API, and related products.
- `Explore`: read-only search across many files.
- `general-purpose`: research and multi-step work.
- `Plan`: designs implementation plans.
- `statusline-setup`: configures the status line.
- `zapier:Zapier MCP Specialist`: plugin-provided. Works through Zapier.

## 7. Planning, questions, worktrees

| Tool | Permission | Here | Parameters | Notes |
|---|---|---|---|---|
| `AskUserQuestion` | No | direct | `questions` (1 to 4), each with 2 to 4 options and `multiSelect` | Questions stay open by default. `askUserQuestionTimeout` (60 s, 5 m, or 10 m) auto-continues. The timer never runs in background sessions, screen-reader mode, or Remote Control. [S6] [S8] |
| `EnterPlanMode` | No | deferred | none | Designs before coding. [S6] [S7] |
| `ExitPlanMode` | Yes | deferred | `allowedPrompts` (deprecated, unused) | Presents the plan for approval. [S6] [S7] |
| `EnterWorktree` | Yes | deferred | `name` or `path` (mutually exclusive) | Creates a worktree under `.claude/worktrees/`. A `path` elsewhere needs approval. [S6] [S7] |
| `ExitWorktree` | No | deferred | `action` (keep or remove), `discard_changes` | Refuses removal when there is uncommitted or unmerged work, unless `discard_changes` is set. [S6] [S7] |

## 8. Scheduling and wakeups

| Tool | Permission | Here | Parameters | Notes |
|---|---|---|---|---|
| `ScheduleWakeup` | No | direct | `delaySeconds` (60 to 3600), `prompt`, `reason`, `noop`, `stop` | Paces a self-paced `/loop`. `stop: true` cancels the pending wakeup. [S6] [S8] |
| `CronCreate` | No | deferred | `cron` (5 fields, local time), `prompt`, `recurring` (default true), `durable` (no effect) | Session-only. Recurring jobs expire after 7 days. Jobs come back on `--resume` or `--continue` if unexpired. [S6] [S7] |
| `CronDelete` | No | deferred | `id` | [S7] |
| `CronList` | No | deferred | none | [S7] |
| `send_later` | (remote) | direct | `message`, `delay_minutes` or `at`, `name`, `initiation` | One-shot message back into this session, at minute granularity. [S8] |
| `create_trigger`, `update_trigger`, `list_triggers`, `get_trigger`, `fire_trigger`, `delete_trigger` | (remote) | direct | As listed in [S8] | Cloud scheduled tasks. Each can fire into this session, a named session, or a fresh session per run. The names differ from RemoteTrigger (Q5). [S8] |

## 9. Skills, discovery, connectors, plugins

| Tool | Permission | Here | Parameters | Notes |
|---|---|---|---|---|
| `Skill` | Yes | direct | `skill`, `args` | Runs a skill in the main conversation. [S6] [S8] |
| `SuggestSkills` | not stated | direct | `keywords`, `trigger` (`proactive` or `user_asked`) | Renders a skill suggestion card. [S8] |
| `ListSkills` | not stated | deferred | `keywords` | Lists enabled skills. [S7] |
| `SearchSkills` | not stated | deferred | `keywords` | Searches the skill catalog. [S7] |
| `ToolSearch` | No | direct | `query` (`select:` or keywords), `max_results` (default 5) | Loads deferred schemas. [S6] [S8] |
| `ListConnectors` | not stated | deferred | `keywords` | Lists connectors and whether each is enabled in this chat. [S7] |
| `SuggestConnectors` | not stated | deferred | `uuids` (1 to 32) | Resolves connector payloads. [S7] |
| `SearchMcpRegistry` | not stated | deferred | `keywords` (1 to 8) | Searches the connector registry. [S7] |
| `ListPlugins` | not stated | deferred | `keywords` | Lists plugins enabled on the account. [S7] |
| `SearchPlugins` | not stated | deferred | `keywords` | Searches the plugin catalog. [S7] |
| `SuggestPluginInstall` | not stated | deferred | `plugins`, `contextLabel`, `trigger` | Renders an install card. [S7] |
| `ShowOnboardingRolePicker` | not stated | direct | none | Cowork onboarding only. [S8] |

## 10. MCP resources

| Tool | Permission | Here | Parameters | Notes |
|---|---|---|---|---|
| `ListMcpResourcesTool` | No | deferred | `server` (optional) | Leaves out MCP Apps UI resources. [S6] |
| `ReadMcpResourceTool` | No | deferred | `server`, `uri` | [S6] [S7] |
| `ReadMcpResourceDirTool` | not stated | deferred | `server`, `uri` | Lists one directory resource on a server that supports it. [S7] |
| `WaitForMcpServers` | No | absent | none | Appears only when tool search is off. [S6] |

## 11. Output, notifications, feedback

| Tool | Permission | Here | Parameters | Notes |
|---|---|---|---|---|
| `SendUserFile` | No | direct | `files`, `caption`, `status` (normal or proactive), `display` (render or attach) | Needs a connected Remote Control client or a cloud session. Not on some providers. [S6] [S8] |
| `PushNotification` | No | deferred | `message` (200 characters at most), `status` (proactive only) | Desktop and phone push. Not on some providers. [S6] [S7] |
| `ReadNotifications` | not stated | direct | none | Reads queued notifications: GitHub events, scheduled triggers, and messages. [S8] |
| `ReportFindings` | No | direct | `findings` (`file`, `line`, `summary`, `short_summary`, `failure_scenario`, `category`, `verdict`, `outcome`), `level` | Structured code-review findings. [S6] [S8] |
| `SendFeedback` | No | absent | none | Drafts a feedback report. Sends nothing until approved. [S6] |

## 12. Artifacts (claude.ai pages)

| Tool | Permission | Here | Parameters | Notes |
|---|---|---|---|---|
| `Artifact` | Yes | direct | `action` (publish, list, read, delete, open, pin, unpin, quickstart), `file_path`, `url`, `files`, `capabilities`, `icon`, `description`, `label`, `edits`, `type_url`, `intent`, `asset`, `from_url`, `asset_ids`, `pin`, `force`, `root`, `scope`, `path`, `out_dir` | Needs a Pro, Max, Team, or Enterprise plan and `/login`. [S6] Republishing updates the same URL. The parameter set is large; see [S8]. |
| `ArtifactComments` | not stated | deferred | `action` (read, reply, resolve, watch), `url`, `thread_id`, `text` (4,096 bytes at most), `cursor`, `on` | Comment text is data, not instructions. [S7] |
| `ArtifactData` | not stated | deferred | `action` (get, list, query, profiles, set, update, str_replace, delete, batch), `url`, `collection`, `doc_id`, `data` or `file_path`, `field`, `old_str`, `new_str`, `if_version`, `query`, `writes` (50 at most), `as_level`, `out_dir` | A per-artifact shared database. Pin writes with `if_version`. [S7] |

## 13. Docs connector

| Tool | Here | Parameters | Notes |
|---|---|---|---|
| `mcp__Claude_Docs__batch` | direct | `container`, `batch`, `opId`, `verbose` | Creates a doc, or applies operations atomically. [S8] |
| `mcp__Claude_Docs__guide` | direct | `items` | Guides by topic. [S8] |
| `mcp__Claude_Docs__update` | direct | `ref`, `payload`, `container`, `answering`, `engine`, `opId`, `verbose` | Edits a tab, renames, or changes a stored value. [S8] |
| `create`, `delete`, `export`, `query`, `read` (`mcp__Claude_Docs__` prefix) | deferred | per [S7] | Connector operations. [S7] |

Rules from [S8]: create a doc only when the user asks for one. The first call is a skeleton. Answer doc comments under the thread's root.

## 14. Remote sessions and environment (direct, 28 tools)

Source: [S8]. Names only; parameters are summarized below.

```
add_repo             archive_session          confirm_repository_trust  create_session
create_trigger       delete_trigger           fire_trigger              get_event
get_session          get_trigger              interrupt_session         list_environments
list_events          list_repos               list_sessions             list_triggers
read_documentation   register_repo_root       send_later                send_message
set_session_tags     set_session_title        subscribe_pr_activity     unarchive_session
unsubscribe_pr_activity  unwatch_url          update_trigger            watch_url
```

Notable parameters [S8]:

- `create_session.permission_mode`: default, plan, acceptEdits, dontAsk, bypassPermissions, or auto. A plan session waits for a person's approval.
- `add_repo.access`: read (the default) or push.
- `subscribe_pr_activity`: `owner`, `repo`, `pullNumber`.
- `send_message.priority`: now, next, or later.
- `watch_url`: returns a webhook URL and a sealed credential. Payloads arrive as messages.
- `read_documentation.topic`: ten environment topics, for example `environment.network` and `session.permissions`.

## 15. Design

| Tool | Here | Parameters | Notes |
|---|---|---|---|
| `DesignSync` | deferred | `method` (11 values), `projectId`, `planId`, `writes`, `deletes`, `files`, `assets`, `counts`, `name`, `path`, `paths`, `localDir` | Only when the user starts `/design-sync`. The schema says standalone Claude Design closes on 2026-12-14. [S7] |

## 16. Connectors and plugin tools (names only, deferred)

| Family | Count | Here | Source |
|---|---|---|---|
| GitHub | 57 | deferred | [S7] |
| Gmail | 32 | deferred | [S7] |
| Notion | 17 | deferred | [S7] |
| alphaXiv | 6 | deferred | [S7] |
| PDF viewer (plugin) | 3 | deferred | [S11]: newly loadable |

GitHub:

```
actions_get  actions_list  actions_run_trigger  add_comment_to_pending_review  add_issue_comment
add_reply_to_pull_request_comment  assign_copilot_to_issue  create_branch  create_or_update_file
create_pull_request  create_pull_request_with_copilot  create_repository  delete_file
disable_pr_auto_merge  enable_pr_auto_merge  fork_repository  get_check_run  get_commit
get_copilot_job_status  get_file_contents  get_job_logs  get_label  get_latest_release  get_me
get_release_by_tag  get_tag  get_team_members  get_teams  issue_read  issue_write  list_branches
list_commits  list_issue_fields  list_issue_types  list_issues  list_pull_requests  list_releases
list_repository_collaborators  list_tags  merge_pull_request  pull_request_read
pull_request_review_write  push_files  request_copilot_review  resolve_review_thread
run_secret_scanning  search_code  search_commits  search_issues  search_pull_requests
search_repositories  search_users  sub_issue_write  unresolve_review_thread  update_issue_comment
update_pull_request  update_pull_request_branch
```

Gmail:

```
apply_sensitive_message_label  apply_sensitive_thread_label  batch_get_messages  batch_get_threads
create_draft  create_label  delete_draft  delete_label  forward  get_draft  get_message  get_thread
label_message  label_thread  list_drafts  list_labels  mark_message_spam  mark_thread_spam  reply
search_threads  send_message  trash_message  trash_thread  unlabel_message  unlabel_thread
unmark_message_spam  unmark_thread_spam  untrash_message  untrash_thread  update_draft
update_label  update_message_labels
```

Notion:

```
notion-calendar-cancel-events  notion-calendar-create-events  notion-calendar-list-calendar-resources
notion-calendar-list-calendars  notion-calendar-list-contacts  notion-calendar-list-coworkers-events
notion-calendar-list-events  notion-calendar-update-events  notion-delete-comment
notion-delete-databases  notion-delete-pages  notion-get-groups  notion-restore-pages
notion-set-comment-reaction  notion-set-discussion-resolved  notion-update-comment
notion-update-enabled-skills
```

alphaXiv:

```
answer_pdf_queries  discover_papers  get_for_you_feed  get_hot_feed  get_paper_content
read_files_from_github_repository
```

PDF viewer (plugin): `display_pdf`, `interact`, `list_pdfs`.

## 17. Demoted and removed names

Demoted, not deleted, so older notes still resolve.

| Name | Status | Source |
|---|---|---|
| `TaskOutput` | Removed in v2.1.277. Use `Read` on the background task's output file. | [S6] |
| `TodoWrite` | Disabled by default. [S6] says `CLAUDE_CODE_ENABLE_TASKS=0` re-enables it in sessions that have the task-tracking tools. | [S6] |
| `--enable-auto-mode` (flag) | Removed in v2.1.111. Use `--permission-mode auto`. | [S4] |
| `--remote` (flag) | Deprecated alias for `--cloud`. | [S4] |
| `Task`, `BashOutput`, `KillBash`, `LS`, `MultiEdit`, `NotebookRead`, `SlashCommand` | Not in [S6] and not in this session. Older releases may have had some of them. | UNVERIFIED |

[S1]: https://code.claude.com/docs/llms.txt
[S2]: https://code.claude.com/docs/en/hooks
[S3]: https://code.claude.com/docs/en/settings
[S4]: https://code.claude.com/docs/en/cli-reference
[S5]: https://code.claude.com/docs/en/slash-commands
[S6]: https://code.claude.com/docs/en/tools-reference
[S7]: CLAUDE-CODE-PKM.md#sources
[S8]: CLAUDE-CODE-PKM.md#sources
[S9]: CLAUDE-CODE-PKM.md#sources
[S10]: https://code.claude.com/docs/en/claude-code-on-the-web
[S11]: CLAUDE-CODE-PKM.md#sources
[SANDBOX-FACTS]: SANDBOX-FACTS.md
