# Harness features

**Snapshot 2026-10-21.** Back to the [hub](CLAUDE-CODE-PKM.md). Tools are in [TOOLS](CLAUDE-CODE-PKM-TOOLS.md). Tags and source IDs are defined in the hub.

## 1. Entry points and session modes

| Feature | How it is used | Tag |
|---|---|---|
| Interactive session | `claude`, or `claude "query"` | VERIFIED [S4] |
| Print mode | `claude -p "query"`, with piped input allowed | VERIFIED [S4] |
| Output formats | `--output-format` takes text, json, or stream-json. `--input-format` takes text or stream-json | VERIFIED [S4] |
| Continue and resume | `-c`, `-r <id or name>`, `--fork-session`, `--session-id`, `-n <name>` | VERIFIED [S4] |
| Background sessions | `--bg`, plus `claude agents` (agent view) and `attach`, `logs`, `respawn`, `rm`, `stop`, `daemon` | VERIFIED [S4]. Agent view: INDEX [agent view](https://code.claude.com/docs/en/agent-view) |
| Restricted, safe, and bare modes | `--restricted` confines file tools, refuses bypass, and refuses to create cloud sessions. `--safe-mode` turns off all customizations. `--bare` skips auto-discovery | VERIFIED [S4] |
| Remote and cloud | `--cloud`, `--teleport`, `--environment`, `--ref`, `--remote-control` (alias `--rc`), `claude remote-control` | VERIFIED [S4]. INDEX: [web](https://code.claude.com/docs/en/claude-code-on-the-web) [S10] |
| Editors and browser | `--ide`, `--chrome`, `--no-chrome`, `--desktop` | VERIFIED [S4] |
| Fast mode | `/fast` toggles faster responses | SESSION [S8]. INDEX: [fast mode](https://code.claude.com/docs/en/fast-mode) |
| Effort | `--effort` takes low, medium, high, xhigh, max, or ultracode. Settings `effortLevel` and `modelSettings` hold the default | VERIFIED [S4] [S3] |
| Advisor | `--advisor` pairs the main model with a stronger advisor, used at key moments | VERIFIED [S4]. INDEX: [advisor](https://code.claude.com/docs/en/advisor) |

## 2. Permission modes

- **Names**: default, acceptEdits, plan, auto, dontAsk, and bypassPermissions. `manual` is an alias for default, from v2.1.200. VERIFIED [S4]. The schema enum in [S7] lists the same six names. SESSION.
- **Starting mode**: `--permission-mode` sets it, and overrides `defaultMode` in settings. VERIFIED [S4].
- **Bypass**: `--dangerously-skip-permissions` equals bypassPermissions. VERIFIED [S4].
- **Shift+Tab cycle**: `--allow-dangerously-skip-permissions` adds bypass to the cycle without starting in it. VERIFIED [S4]. Auto mode is in the cycle by default, per the removed-flag note in [S4].
- **Settings limit**: `permissions.defaultMode` values `auto` and `bypassPermissions` do not take effect from project or local files. VERIFIED [S3].
- **Plan mode**: `ExitPlanMode` asks for approval. VERIFIED [S6]. A plan session created remotely waits for a person to approve it. SESSION [S7].
- **Unattended runs**: `--permission-prompts none` denies prompts that nobody can answer. `--permission-prompt-tool` names an MCP tool that answers them instead. VERIFIED [S4].
- **Auto mode classifier**: decides the prompts for Monitor commands and WebSocket opens. VERIFIED [S6].

## 3. Permission rules

- **Form**: `ToolName(specifier)` in `allow`, `ask`, and `deny` lists, or in the `/permissions` interface. VERIFIED [S6] [S3].
- **Examples**: `Bash(npm run *)`, `Read(~/secrets/**)`, `Edit(/src/**)`, `Skill(deploy *)`, `Agent(Explore)`, `WebFetch(domain:example.com)`, and bare `WebSearch`. VERIFIED [S6].
- **Edit and Read**: an `Edit` allow also grants read on the same path. A `Read` deny also blocks `Edit` and `Write` there. VERIFIED [S6].
- **Bash and PowerShell**: on Windows with Git Bash, a Bash deny also turns PowerShell off, unless `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` or a PowerShell rule is set. VERIFIED [S6].
- **Merging**: lists merge across scopes, and scalar keys override. VERIFIED [S3].
- **Trust**: allow rules in a project file wait for workspace trust. Deny and ask rules apply right away. VERIFIED [S3].
- **Saved approvals**: "Yes, and don't ask again" writes an allow rule to `.claude/settings.local.json`. VERIFIED [S3].
- **Managed exceptions**: a few restrictive values win from lower scopes. Examples: `disableClaudeAiConnectors: true`, `enableArtifact: false`, and `isolatePeerMachines: true`. VERIFIED [S3].
- **Flags**: `--allowedTools` runs named tools without prompts. `--disallowedTools` removes tools or denies patterns. `--tools` restricts the built-in set. VERIFIED [S4] [S6].

## 4. Settings

| Scope | File | Shared through git? | Tag |
|---|---|---|---|
| User | `~/.claude/settings.json` | no | VERIFIED [S3] |
| Shared project | `.claude/settings.json` | yes; commit it | VERIFIED [S3] |
| Project local | `.claude/settings.local.json` | no. Claude Code adds it to the global git excludes the first time it writes the file | VERIFIED [S3] |
| Managed | `managed-settings.json`, device policy, or server-managed settings | organization-wide | VERIFIED [S3] |
| Global config | `~/.claude.json`: sign-in, MCP server configs, trust decisions, global keys | no | VERIFIED [S3] |

- **Precedence**, highest first: managed settings, then the `--settings` flag, then project local, then shared project, then user. VERIFIED [S3].
- **Environment variables** are not a level. Each variable and key pair has its own rule. VERIFIED [S3].
- **Home directory**: `CLAUDE_CONFIG_DIR` moves the home config folder. VERIFIED [S3].
- **Live reload**: most edits apply without a restart, including permissions, hooks, and `apiKeyHelper`. A settings file created mid-session loads if its folder existed at start. Some keys are read only at start. VERIFIED [S3]. The hook case conflicts with repo observations (Q1).
- **In-session tools**: `/config` writes to user or local settings, and `/config key=value` sets one option. `/status` lists the `Setting sources`. `claude doctor` lists rejected entries. VERIFIED [S3].
- **Broken files**: a Settings Error opens a dialog at start. A Settings Warning skips the bad entry. Invalid managed entries are dropped, and the rest keeps being enforced. In `-p` runs, a broken file is skipped. VERIFIED [S3].
- **Cloud sessions**: user and local files are not read. A repo's `.claude/settings.json` is read in a single-repo cloud session. Device-level managed files do not reach cloud sessions. VERIFIED [S3].
- **Editor support**: a published JSON schema, referenced by `$schema`, gives validation and autocomplete. VERIFIED [S3].

## 5. Hooks

### Events (33)

VERIFIED [S2].

- **Session**: `SessionStart` (matchers: startup, resume, clear, compact, fork), `Setup` (matchers: init, maintenance), `SessionEnd`.
- **Prompts**: `UserPromptSubmit`, and `UserPromptExpansion` (matches the command name).
- **Tools**: `PreToolUse` (can block), `PermissionRequest`, `PermissionDenied`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`.
- **Display and notifications**: `Notification` (13 matcher types, such as `permission_prompt` and `idle_prompt`), and `MessageDisplay`.
- **Agents and tasks**: `SubagentStart` (matches the agent type), `SubagentStop`, `TaskCreated`, `TaskCompleted`, `TeammateIdle`.
- **Turn end**: `Stop`, and `StopFailure` (matches API error types).
- **Config and files**: `InstructionsLoaded`, `ConfigChange`, `CwdChanged`, `DirectoryAdded`, `FileChanged`.
- **Worktrees**: `WorktreeCreate` (replaces the default git behavior), `WorktreeRemove`.
- **Compaction and models**: `PreCompact`, `PostCompact` (matchers: manual, auto), `PreModelSwitch` (can block), `PostModelSwitch`.
- **MCP input**: `Elicitation`, `ElicitationResult`.

### Matchers

VERIFIED [S2].

- An empty matcher, `*`, or no matcher matches everything.
- Letters, digits, `_`, `-`, spaces, `,`, and `|` form an exact name or a list.
- Anything else is an unanchored JavaScript regex. `Edit.*` matches `NotebookEdit`, so use `^Edit$` for a whole-name match.
- MCP tools are named `mcp__<server>__<tool>`. Plugin-bundled servers use `mcp__plugin_<plugin>_<server>__<tool>`.
- The `if` field takes a permission-rule expression, such as `Bash(git *)`. It runs only on five tool events: PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, and PermissionDenied.

### Configuration

VERIFIED [S2].

- **Three levels**: event, then matcher group, then handler list. Entries from every level merge.
- **Locations**: user settings; `.claude/settings.json`; `.claude/settings.local.json`; managed policy; a plugin's `hooks/hooks.json`; skill frontmatter (active for the rest of the session once the skill runs); subagent frontmatter (active while that subagent runs; `Stop` becomes `SubagentStop`).
- **Handler types**: `command`, `http`, `mcp_tool`, `prompt`, and `agent` (experimental). `SessionStart` accepts only `command` and `mcp_tool`.
- **Command fields**: `command`, `args` (exec form, no shell), `shell` (bash or powershell), `async`, `asyncRewake`, `timeout`, `statusMessage`, `onFailure` (continue or block), and `if`.
- **Other fields**: HTTP takes `url`, `headers`, and `allowedEnvVars`. MCP tool takes `server`, `tool`, and `input`. Prompt and agent take `prompt` and `model`. Skill frontmatter alone takes `once`.

Example from [S2]:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh",
            "args": [],
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Input (stdin)

VERIFIED [S2]. Partial: most per-event schemas were not in the fetched answer.

- **Common fields**: `session_id`, `prompt_id`, `transcript_path`, `cwd`, `scratchpad_dir` (v2.1.257 or later), `permission_mode`, `effort` (with a `level` field), `hook_event_name`, `agent_id`, `agent_type`.
- **Event fields seen**: PreToolUse gets `tool_name`, `tool_input`, `tool_use_id`. Stop and SubagentStop get `last_assistant_message`. PreModelSwitch and PostModelSwitch get `from_model` and `to_model`. SessionStart gets `source`.

### Exit codes

VERIFIED [S2].

- **0**: success. A single JSON object on stdout is parsed. Plain stdout reaches Claude's context only on UserPromptSubmit, UserPromptExpansion, SessionStart, and PostModelSwitch. Stderr from an exit-0 hook never reaches Claude.
- **2 blocks** on PreToolUse, UserPromptSubmit, UserPromptExpansion, PreModelSwitch, PreCompact, Stop, SubagentStop, TeammateIdle, TaskCreated, TaskCompleted, ConfigChange (except policy settings), PostToolBatch, Elicitation, ElicitationResult, WorktreeCreate, and WorktreeRemove.
- **2 does not block** on PostToolUse and PostToolUseFailure (stderr goes to Claude), PermissionRequest (use `decision`), PermissionDenied (use `retry`), StopFailure, Notification, Setup, InstructionsLoaded, SessionStart, SubagentStart, SessionEnd, and others.
- **Other non-zero codes** are non-blocking errors. The action goes ahead unless `onFailure` is `block`.
- **Timeouts**: command, HTTP, and MCP-tool hooks are cancelled at their timeout, and their output is dropped. On PreToolUse a timeout does not block. On PreModelSwitch it does.

### Output (decisions)

VERIFIED [S2].

- **Universal fields**: `continue` (false stops Claude), `stopReason`, `suppressOutput`, `systemMessage`, `terminalSequence`.
- **PreToolUse**: `hookSpecificOutput.permissionDecision` takes allow, deny, ask, or defer. Also `permissionDecisionReason` and `updatedInput`.
- **PermissionRequest**: `hookSpecificOutput.decision.behavior` takes allow or deny.
- **SessionStart**: `additionalContext`, `initialUserMessage`, `sessionTitle`, `watchPaths`, `reloadSkills`.
- **Top-level `decision: "block"`**: several events use it, including UserPromptSubmit, PostToolUse, Stop, ConfigChange, and PreCompact.
- **Size cap**: `additionalContext`, `systemMessage`, `initialUserMessage`, and plain stdout are each capped at 10,000 characters.

### Timeouts and environment

VERIFIED [S2].

- **Defaults**: command, HTTP, and MCP tool 600 s. Prompt 30 s. Agent 60 s. UserPromptSubmit, PreModelSwitch, and PostModelSwitch 30 s. MessageDisplay 10 s. SessionEnd shares a 1.5 s budget, raised to match a longer per-hook timeout of up to 60 s.
- **Variables for command hooks**: `CLAUDE_PROJECT_DIR` is the project root where the session started. It does not move into a worktree. `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, and `CLAUDE_PLUGIN_OPTION_<KEY>` serve plugins. `CLAUDE_ENV_FILE` (SessionStart only) takes `export` lines that persist into later Bash commands. `CLAUDE_EFFORT`, `CLAUDE_CODE_REMOTE` (`"true"` in remote web environments), and `CLAUDE_CODE_BRIDGE_SESSION_ID` are also set.
- **Not provided**: there is no `$CLAUDE_MODEL`. Follow model changes with PostModelSwitch.
- **Kill switches**: `disableAllHooks`, `allowManagedHooksOnly`, `allowedHttpHookUrls`, and `httpHookAllowedEnvVars`. VERIFIED [S2].

### Observations in this repo

REPO [S9].

- The repo's `.claude/settings.json` registers a SessionStart hook, according to [SANDBOX-FACTS](SANDBOX-FACTS.md). The file is present. It was not re-read in this pass.
- In one session, a hook added to `.claude/settings.local.json` mid-session produced no evaluation. That conflicts with [S3] (Q1). Source: [OPEN-PROBLEMS](OPEN-PROBLEMS.md) P-dae1.
- A user-level Stop hook, outside the repo, ran at turn end. Its exit-2 stderr reached the model as "Stop hook feedback" ([SANDBOX-FACTS](SANDBOX-FACTS.md), 2026-10-17).
- A disarmed hook added 55.2 ms per tool call, as a mean of 20 runs in one container ([SANDBOX-FACTS](SANDBOX-FACTS.md)).

## 6. Memory

- **Persistent instructions** live in CLAUDE.md or AGENTS.md. Auto memory is automatic. INDEX: [memory](https://code.claude.com/docs/en/memory).
- **Load events**: CLAUDE.md and `.claude/rules/*.md` enter context with a reason: `session_start`, `nested_traversal`, `path_glob_match`, `include`, or `compact`. VERIFIED [S2] (InstructionsLoaded).
- **Lazy loads**: a subdirectory's CLAUDE.md and path-scoped rules also load when Claude views a file through `cat`, `grep`, `sed -n`, and similar commands. VERIFIED [S6] (Edit notes).
- **Dynamic context**: `--exclude-dynamic-system-prompt-sections` moves per-user context, such as the auto-memory location, out of the system prompt. VERIFIED [S4].
- **In this session**: the project CLAUDE.md arrives as an injected reminder that names its path. SESSION [S8].
- **Connector memory**: a memory store reached through a connector is separate from Claude Code memory. SESSION [S8].
- **Not read**: CLAUDE.md import syntax, the rules-folder details, and the auto-memory location (Q8).

## 7. Commands and skills

### Built-in commands

- **With descriptions** in [S5]: `/permissions`, `/add-dir`, `/cd` (v2.1.246 or later), `/usage`, `/cost` (an alias of `/usage`), `/rewind`, `/status`, `/skills`, `/context`, `/plugin`, `/reload-plugins`, `/reload-skills`, `/skill-doctor`. VERIFIED [S5].
- **Named without a description** in [S5]: `/help`, `/compact`, `/model`, `/login`, `/feedback` (terminal only), `/init`, `/security-review`. VERIFIED [S5].
- **Bundled skills** run with a slash: `/doctor` (alias `checkup`), `/verify`, `/run`, `/run-skill-generator`, `/claude-api`, and `/workflow-authoring` (only when dynamic workflows are enabled). VERIFIED [S5].
- **Also named** in [S5]: `/batch`, `/debug`, `/loop`, `/simplify`, and `/code-review` (alias `/review`, which runs as a forked subagent). VERIFIED [S5].
- **Named elsewhere**: `/schedule` backs RemoteTrigger, `/list-agents` backs ListAgents, and `/tasks` lists background tasks [S6]. `/autocompact` accepts the same values as the `--autocompact` flag [S4]. `/goal` sets a completion condition. INDEX: [goal](https://code.claude.com/docs/en/goal).
- **Full list**: [Commands](https://code.claude.com/docs/en/commands) (INDEX, not fetched; Q8).

### Custom commands and skills

VERIFIED [S5] unless marked.

- **Locations**: project `.claude/skills/<name>/SKILL.md` (the older `.claude/commands/<name>.md` still works). Personal `~/.claude/skills/<name>/SKILL.md`.
- **Names**: plugin skills are `/<plugin>:<skill>`. A nested folder such as `apps/web/.claude/skills/deploy` becomes `/apps/web:deploy` only when its name clashes. Command subfolders give `/frontend:component`. Synced claude.ai skills use `/anthropic-skills:<name>`.
- **Collisions**: enterprise beats personal, and personal beats project. A skill beats a command file with the same name.
- **Frontmatter**: `name`, `description` (the first body line is used if absent), `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context` (`fork`), `agent`, `background`, `hooks`, `paths`, `shell`, `metadata`, `license`, and `compatibility`. Outside Claude Code, only six keys are accepted: `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools`.
- **Listing budget**: `description` plus `when_to_use` is cut at 1,536 characters.
- **Placeholders**: `$ARGUMENTS`, `$ARGUMENTS[N]`, `$N`, and `$name` (for names declared in `arguments`). A backslash escapes a dollar sign. `${CLAUDE_SESSION_ID}` and `${CLAUDE_SKILL_DIR}` are separate substitutions.
- **Cost check**: `/skill-doctor` reports what each skill costs in context and how often it is used.
- **Invocation**: when the user types `/<name>`, the session runs it through the Skill tool. SESSION [S8]. Claude also loads a skill on its own when its description fits, unless `disable-model-invocation` is set. VERIFIED [S5].
- **This session's listing** has 78 entries: `anthropic-skills` 21, `engineering` 10, `data` 10, `design` 7, `pdf-viewer` 5, `productivity` 4, `zapier` 4, and 17 without a namespace. SESSION [S8].

## 8. Subagents and agent types

- **Agent tool**: spawns a subagent with its own context, which returns one final result. VERIFIED [S6].
- **Background by default**: foreground subagents show permission prompts in place. Background subagents send them to the main session, where Esc denies one call. VERIFIED [S6].
- **Limits**: `tools` and `disallowedTools` set the subagent's tools, and `disallowedTools` wins when both are set. `maxTurns` caps the turns. A subagent can be resumed by agent ID or name. VERIFIED [S6].
- **Fork**: inherits the full conversation. VERIFIED [S6].
- **Teammates**: launched with a `name` when agent teams are on. VERIFIED [S6].
- **CLI**: `--agents` defines subagents from JSON. `--agent` picks one for the session. `--append-subagent-system-prompt` (or `-file`) adds text to subagent prompts in `-p` mode. VERIFIED [S4].
- **Hooks**: SubagentStart matches the agent type, such as `general-purpose`, `Explore`, `Plan`, custom names, or plugin-scoped names. SubagentStop fires when the subagent finishes. VERIFIED [S2].
- **Nesting**: subagents can spawn subagents. INDEX (What's new digest).
- **Definition files and frontmatter**: INDEX: [sub-agents](https://code.claude.com/docs/en/sub-agents). Not fetched (Q8).
- **Agent types**: seven, listed in [TOOLS §6](CLAUDE-CODE-PKM-TOOLS.md#6-agents-and-orchestration). SESSION [S8].

## 9. Plugins, marketplaces, mods

- **Plugin**: a bundle of skills, hooks, MCP servers, agents, and output styles. INDEX: [overview](https://code.claude.com/docs/en/plugins/overview).
- **Components**: `/reload-plugins` applies changes to a plugin's `hooks/`, `.mcp.json`, `agents/`, and `output-styles/`. VERIFIED [S5]. Plugin hooks live in `hooks/hooks.json`. VERIFIED [S2].
- **Names**: plugin skills use `/<plugin>:<skill>` [S5]. Plugin MCP tools use `mcp__plugin_<plugin>_<server>__<tool>` [S2].
- **CLI**: `claude plugin` (alias `plugins`). `--plugin-dir` loads a directory or `.zip` for one session. `--plugin-url` fetches a `.zip` for one session. VERIFIED [S4].
- **In session**: `/plugin` manages installs and marketplaces. `/reload-plugins` applies changes. VERIFIED [S5].
- **Marketplaces and evals**: INDEX: [install](https://code.claude.com/docs/en/plugins/install), [marketplaces](https://code.claude.com/docs/en/plugins/anthropic-marketplaces), [publish](https://code.claude.com/docs/en/plugins/publish), and `claude plugin eval` (What's new digest).
- **Mods**: panes, commands, tool-call rules, and a hooks module, with organization controls. INDEX: [mods overview](https://code.claude.com/docs/en/plugins/mods/overview). SESSION: a plugin-authoring skill covers mods [S8].
- **Code intelligence**: the LSP tool needs a code-intelligence plugin. VERIFIED [S6].
- **In this session**: plugin discovery tools are `ListPlugins`, `SearchPlugins`, and `SuggestPluginInstall` [TOOLS §9](CLAUDE-CODE-PKM-TOOLS.md#9-skills-discovery-connectors-plugins).

## 10. MCP

- **CLI**: `claude mcp` configures servers. `claude mcp login <name>` runs an OAuth flow for HTTP, SSE, and claude.ai connector servers. `claude mcp logout <name>` clears stored credentials. VERIFIED [S4].
- **Flags**: `--mcp-config` loads servers from JSON files or strings. With `-p`, it waits up to `MCP_TIMEOUT` (30 s by default) for pending servers. `--strict-mcp-config` ignores all other MCP configs. VERIFIED [S4].
- **Tool search**: MCP tool schemas load on demand through ToolSearch. VERIFIED [S6].
- **Resources**: `ListMcpResourcesTool`, `ReadMcpResourceTool`, and `ReadMcpResourceDirTool`. Listings leave out MCP Apps UI resources. VERIFIED [S6] [S7].
- **Channels**: an MCP server can push events into a live session. `--channels` is a research-preview flag. VERIFIED [S4]. INDEX: [channels](https://code.claude.com/docs/en/channels).
- **Managed MCP**: managed config files with allow and deny lists. INDEX: [managed MCP](https://code.claude.com/docs/en/managed-mcp).
- **Session state**: some servers in this session needed authorization or failed to connect. SESSION [S11]. They are not named here (Q15).
- **Hooks for MCP**: `Elicitation` and `ElicitationResult`. VERIFIED [S2].

## 11. Output, status line, keys, terminal

- **Output styles**: built-in styles such as Concise and Explanatory, or your own. INDEX: [output styles](https://code.claude.com/docs/en/output-styles).
- **Display flags**: `--verbose` overrides the `viewMode` setting. `--prompt-suggestions` emits a predicted next prompt in stream output. VERIFIED [S4].
- **Status line**: a custom bar that shows context use, costs, and git status. INDEX: [status line](https://code.claude.com/docs/en/statusline). SESSION: a `statusline-setup` agent [S8].
- **Keybindings**: a keybindings file remaps shortcuts. INDEX: [keybindings](https://code.claude.com/docs/en/keybindings). SESSION: a keybindings skill points to `~/.claude/keybindings.json` [S8]. The shortcut list was not fetched (Q8).
- **Terminal**: Shift+Enter setup, the bell, tmux, theme, and Vim mode. INDEX: [terminal config](https://code.claude.com/docs/en/terminal-config).
- **Accessibility**: `--ax-screen-reader`, the `axScreenReader` setting, and `CLAUDE_AX_SCREEN_READER`. VERIFIED [S4]. The question timer does not run in screen-reader mode. VERIFIED [S6].
- **Other**: fullscreen rendering and voice dictation. INDEX: [fullscreen](https://code.claude.com/docs/en/fullscreen), [voice dictation](https://code.claude.com/docs/en/voice-dictation).

## 12. Context, compaction, cost, effort

- **Summarizing**: when the conversation grows long, older context is summarized. SESSION [S8].
- **Compaction hooks**: PreCompact and PostCompact, with `manual` or `auto` matchers. VERIFIED [S2].
- **Commands and flags**: `/compact` (named in [S5]). `--autocompact` takes `auto` or a token count, and `/autocompact` takes the same values. VERIFIED [S4]. Window settings: INDEX: [model config](https://code.claude.com/docs/en/model-config).
- **Caching**: why `/compact` and model switches cost what they cost. INDEX: [prompt caching](https://code.claude.com/docs/en/prompt-caching).
- **Cost**: `/usage`, with `/cost` as an alias [S5]. `--max-budget-usd` caps spend in print mode, and subagent spend counts toward the cap. The cap can be exceeded, so leave headroom. VERIFIED [S4].
- **Monitoring**: OpenTelemetry. INDEX: [monitoring](https://code.claude.com/docs/en/monitoring-usage). Analytics dashboard. INDEX: [analytics](https://code.claude.com/docs/en/analytics).
- **Token readout**: this session shows a remaining-token figure in its context. What it measures and how it refreshes are UNVERIFIED [S8].
- **Effort**: `--effort` is listed in §1. Settings `effortLevel` and `modelSettings` hold the default. VERIFIED [S4] [S3].

## 13. Checkpointing and rewind

- `/rewind` restores files that Claude edited in the conversation. VERIFIED [S5].
- A later release let `/rewind` go back to before `/clear` (What's new digest). INDEX: [checkpointing](https://code.claude.com/docs/en/checkpointing).

## 14. Background work, loops, scheduling

- **Background commands**: `run_in_background` starts a command that keeps running. `/tasks` lists and stops them. VERIFIED [S6].
- **Time limits**: 30 minutes by default, capped at 2 hours. These limits apply only in unattended runs (print mode, SDK, CI, cloud). A local terminal session has none. VERIFIED [S6].
- **Monitor**: deadline 5 minutes by default, at most 30 minutes. A monitor stops with the subagent that started it. VERIFIED [S6].
- **Self-paced loops**: `/loop` paces itself through ScheduleWakeup, between 60 and 3,600 seconds. VERIFIED [S6] [S7] [S8].
- **CronCreate**: session-only. Recurring jobs expire after 7 days. Jobs come back on `--resume` if they have not expired. VERIFIED [S6] [S7].
- **Remote scheduled tasks**: the `create_trigger` family [S8], and RemoteTrigger in the official table [S6] (Q5). INDEX: [scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks) and [routines](https://code.claude.com/docs/en/routines).
- **One-shot messages**: `send_later` [S8].
- **Goal mode**: `/goal` keeps Claude working toward a completion condition. INDEX: [goal](https://code.claude.com/docs/en/goal).
- **Agent view**: `claude agents` shows and dispatches parallel background sessions. VERIFIED [S4]. INDEX: [agent view](https://code.claude.com/docs/en/agent-view).

## 15. Multi-agent: workflows, teams, messaging

- **Workflow tool**: runs a script that orchestrates many subagents in the background and returns one consolidated result. VERIFIED [S6].
- **Opt-in**: any of these turns workflows on: the keyword "ultracode" in the user's prompt, an explicit request to run a workflow, a skill or command that calls the tool, or a named saved workflow. Default size guideline: under 10 agents. `/config` has a "Dynamic workflow size" setting. SESSION [S8].
- **Script shape**: `export const meta` as a literal, then helpers `agent()`, `parallel()`, `pipeline()`, and `phase()`. Resume with `resumeFromRunId`. SESSION [S7] [S8].
- **Ultracode effort**: `--effort ultracode` requests xhigh effort with ultracode turned on (v2.1.203 or later). VERIFIED [S4]. What else it changes is open (Q7).
- **Agent teams**: `--teammate-mode` takes in-process, auto, tmux, or iterm2. VERIFIED [S4]. Hooks: TeammateIdle, TaskCreated, and TaskCompleted. VERIFIED [S2]. INDEX: [agent teams](https://code.claude.com/docs/en/agent-teams).
- **Cross-session messaging**: ListAgents and SendMessage. VERIFIED [S6]. INDEX: [cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging).

## 16. Headless and SDK

- **Print mode**: `-p` runs one prompt and exits. Output formats are in §1. VERIFIED [S4].
- **Limits**: `--max-turns`, `--max-budget-usd`, and `--json-schema` (validated output). `--permission-prompts none` denies prompts. VERIFIED [S4].
- **Startup**: `--bare` skips auto-discovery. `--init`, `--init-only`, and `--maintenance` run Setup hooks. VERIFIED [S4] [S2].
- **Background work at exit**: a `-p` run stays open until its background commands finish or reach their limit. The default is 10 minutes when the prompt is passed as text. VERIFIED [S6].
- **Resumed ended sessions**: resuming an ended session with `-p` exits with code 1. VERIFIED [S6].
- **SDK**: INDEX: [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview). Pages cover sessions, hooks, permissions, MCP, subagents, plugins, cost tracking, structured outputs, and hosting. None were fetched.
- **Flag names**: see §22.

## 17. Cloud, remote, and integrations

- **Claude Code on the web**: cloud sessions from a browser, phone, desktop, or terminal. `--cloud` and `--teleport` move them. INDEX: [claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web) [S10].
- **Cloud environments**: network access levels, environment variables, setup scripts, and caching. INDEX: [cloud environments](https://code.claude.com/docs/en/cloud-environments).
- **Self-hosted**: INDEX: [self-hosted environments](https://code.claude.com/docs/en/self-hosted-environments). The `claude self-hosted-runner` subcommand is VERIFIED [S4].
- **Settings in cloud sessions**: see §4. VERIFIED [S3].
- **Remote Control**: continue a local session from a phone, tablet, or browser. INDEX: [remote control](https://code.claude.com/docs/en/remote-control). The flags are VERIFIED [S4].
- **Integrations** (INDEX): VS Code, JetBrains, the desktop app, mobile, Chrome, computer use from the CLI on macOS, Slack, Claude Tag, GitHub Actions, and GitLab CI/CD. Pages are linked from [S1].
- **Deep links**: a `claude-cli://` link opens a session with a repo and prompt. INDEX: [deep links](https://code.claude.com/docs/en/deep-links).

## 18. Code review and security

- **Local review**: `/code-review` runs as a forked subagent [S5]. The skill takes `--comment`, `--fix`, and `--max-findings` [S8]. INDEX: [local review](https://code.claude.com/docs/en/code-review-local).
- **Ultrareview**: `claude ultrareview [target]` prints findings and exits 0 or 1. Flags: `--json`, `--timeout` (45 minutes by default), and `--post`, which posts a plain PR comment. VERIFIED [S4]. INDEX: [ultrareview](https://code.claude.com/docs/en/ultrareview).
- **Code review on PRs** (Team and Enterprise plans): INDEX: [code review](https://code.claude.com/docs/en/code-review).
- **Structured findings**: the ReportFindings tool. VERIFIED [S6].
- **Security plugins**: security-guidance and Claude Security. INDEX: [security guidance](https://code.claude.com/docs/en/security-guidance), [Claude Security](https://code.claude.com/docs/en/claude-security).

## 19. Git and PR workflow rules (this session)

From [S8] (system prompt):

- Develop on the designated branch. Commit with descriptive messages. Push with `-u`.
- Retry network failures only, with exponential backoff (2, 4, 8, 16 seconds).
- After a push, open a ready-for-review PR if none is open. Mirror a PR template if the repo has one.
- Subscribe to PR events after creating a PR.
- Never rewrite others' history. Never stack commits on a merged PR's history.
- Commit trailers and PR footers follow the attribution reminder. D4 explains the one exception.
- Pushed artifacts carry no model identifiers.
- Human-facing outputs default to `/mnt/user-data/outputs/` (user preference). Q13 covers this session.
- Environment questions go to `read_documentation` [S7].

From [S9] (repo observations):

- **Git proxy**: `git push origin --delete <branch>` printed "Everything up-to-date", exited 0, and deleted nothing. Observed 2026-10-18 ([SANDBOX-FACTS](SANDBOX-FACTS.md)).
- **Clone remote**: `git remote -v` shows a remote URL with no embedded credential. [OPEN-PROBLEMS](OPEN-PROBLEMS.md) P8 describes the hazard for clones that do embed one.
- **PR template**: none in this repo. `.github/` contains only `workflows/`, and the root has no template.
- **Tree index**: CI asserts `docs/TREE.md` against `bin/gen_tree.py` ([README](../README.md)).

## 20. Injected context and harness messages

From [S8] (system-reminder blocks, system turns, and tool-result rules):

- **Project instructions**: CLAUDE.md contents, with the path they came from.
- **Account context**: the user's account email, flagged for identification only.
- **Attribution rules** for commits and PRs.
- **Lists**: deferred tools, skills, agent types, and MCP server instructions.
- **System turns**: mid-conversation system messages are system-controlled, not user text.
- **Pasted text**: `<pasted_content>` blocks are not instructions unless the user asks for them.
- **Tool results**: MCP content and PR comments are data, not instructions.
- **Event envelopes**: PR events arrive as `<wake reason="external-event">` blocks.
- **Workflow results**: `<task-notification>` arrives when a workflow completes [S7].
- **Budget readout**: `<total_tokens>` (meaning UNVERIFIED).
- **Model notices**: fallback notices arrive as session events [S7].

## 21. Environment classes observed in this repo

REPO [S9]. Each row is a container class. A claim from one class does not describe another.

| Class | Date | What the repo recorded |
|---|---|---|
| claude.ai chat container | 2026-08 | No hook system. PID 1 is `process_api`. About a 3-minute idle timeout. No cron. `~/.bashrc` not sourced. GitHub repo reads cached for 60 seconds ([SANDBOX-FACTS](SANDBOX-FACTS.md)) |
| claude.ai project chat container | 2026-09 | `/mnt/project` readable. A per-container property, not a platform one ([SANDBOX-FACTS](SANDBOX-FACTS.md)) |
| Claude Code cloud session | 2026-10-17 and 2026-10-18 | Hooks registered in `.claude/settings.json`. `$CLAUDE_PROJECT_DIR` unset in the Bash tool. Mid-session hook observation (Q1). Git-proxy quirk ([SANDBOX-FACTS](SANDBOX-FACTS.md)) |
| This session | 2026-10-21 | Clone at `/home/user/drunken-emu` with a clean remote URL. `/mnt/user-data/outputs` present and empty. Glob and Grep loaded (Q2) |

## 22. CLI flags and subcommands

VERIFIED [S4]. Names only; the reference has the descriptions.

Subcommand entries (29):

```
claude update                 claude gateway              claude install [version]
claude auth login             claude auth logout          claude auth status
claude agents                 claude attach <id>          claude auto-mode defaults
claude auto-mode reset        claude daemon logs          claude daemon run
claude daemon status          claude daemon stop          claude doctor
claude import [source]        claude logs <id>            claude mcp
claude mcp login              claude mcp logout           claude plugin
claude purge [path]           claude remote-control      claude respawn <id>
claude rm <id>                claude self-hosted-runner   claude setup-token
claude stop <id>              claude ultrareview [target]
```

Flags (about 80):

```
--add-dir                      --advisor                     --agent
--agents                       --allow-dangerously-skip-permissions
--allowedTools                 --append-subagent-system-prompt
--append-subagent-system-prompt-file                         --append-system-prompt
--append-system-prompt-file    --autocompact                 --ax-screen-reader
--bare                         --betas                       --bg
--channels                     --chrome                      --cloud
--continue                     --dangerously-load-development-channels
--dangerously-skip-permissions --debug                       --debug-file
--desktop                      --disable-slash-commands      --disallowedTools
--effort                       --enable-auto-mode (removed)  --environment
--exclude-dynamic-system-prompt-sections                     --exec
--fallback-model               --fork-session                --forward-subagent-text
--from-pr                      --ide                         --init
--init-only                    --include-hook-events         --include-partial-messages
--input-format                 --json-schema                 --maintenance
--max-budget-usd               --max-turns                   --mcp-config
--model                        --name                        --no-chrome
--no-session-persistence       --output-format               --permission-mode
--permission-prompt-tool       --permission-prompts          --plugin-dir
--plugin-url                   --print                       --prompt-suggestions
--ref                          --remote (deprecated)         --remote-control
--remote-control-session-name-prefix                         --replay-user-messages
--restricted                   --resume                      --safe-mode
--session-id                   --setting-sources             --settings
--strict-mcp-config            --system-prompt               --system-prompt-file
--system-prompt-snapshot       --teleport                    --teammate-mode
--tmux                         --tools                       --verbose
--version                      --worktree
```

Short aliases: `-c`, `-n`, `-p`, `-r`, `-v`, `-w`, and `--rc` for `--remote-control`.

## 23. Change history

- **Changelog**: release notes by version. INDEX: [changelog](https://code.claude.com/docs/en/changelog).
- **Weekly digest**: What's new, with entries from Week 13 through Week 37 of 2026 in the index. INDEX: [what's new](https://code.claude.com/docs/en/whats-new/index). The entries were not expanded here. Some name features that appear above, such as dynamic workflows, `claude plugin eval`, and the agent view.

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
[OPEN-PROBLEMS]: OPEN-PROBLEMS.md
[SANDBOX-FACTS]: SANDBOX-FACTS.md
[README]: ../README.md
