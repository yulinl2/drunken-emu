# Directory tree index

*v0.2.0 · 2026-08-31 · generated, CI-asserted*

Canonical copy of the tracked file set. The README carries a **curated** subset
with one-line annotations for landing readers; that one is deliberately partial
and is not generated. This one is exact.

Source of truth is `git ls-files`, so the tree means precisely *what a clone
receives*. Untracked working files (`out/*.png`, `harness/app.jsx`, `__pycache__`)
are absent by construction rather than by an exclusion list that can go stale.

```
python3 bin/gen_tree.py --write     # regenerate this block
python3 bin/gen_tree.py --check     # exit 1 on drift; runs in CI
```

*Why generated:* until v0.2.0 this file carried the command
`tree -I 'out|__pycache__|.git' --dirsfirst`, which **cannot** produce the
content that sat below it — `tree` hides dotfiles without `-a`, so `.github/`
and `.gitignore` were invisible to it, and nothing compared the two. The index
drifted through three commits before anyone re-ran it. A regeneration command
that is never executed is not a regeneration command.

```text
.
|-- .claude/
|   `-- settings.json
|-- .github/
|   `-- workflows/
|       `-- claims.yml
|-- bin/
|   |-- apply_doi.sh
|   |-- blocker_check.py
|   |-- emu
|   |-- figpipe
|   |-- gen_tree.py
|   `-- sync_artifact.py
|-- checks/
|   |-- fixtures/
|   |   |-- chains/
|   |   |   |-- draft_publish_hw2.json
|   |   |   |-- hw1_correction_pass.json
|   |   |   |-- hw1_correction_pass_fixed.json
|   |   |   |-- hw1_correction_pass_transcribed.json
|   |   |   |-- tapgrade_0_6_6.json
|   |   |   |-- tapgrade_0_6_7_sample_pass.json
|   |   |   `-- worked_example.json
|   |   |-- fragment_links_clean.jsx
|   |   |-- fragment_links_nolinks.jsx
|   |   `-- fragment_links_planted.jsx
|   |-- hw2_sample_prediction/
|   |   |-- __init__.py
|   |   |-- __main__.py
|   |   |-- chains.py
|   |   |-- changes.py
|   |   |-- cites.py
|   |   |-- events.py
|   |   |-- inputs.py
|   |   |-- markdown.py
|   |   |-- rebuild.py
|   |   `-- registration.py
|   |-- __init__.py
|   |-- affordances.py
|   |-- blind_audit.py
|   |-- browser.py
|   |-- chain.py
|   |-- chain_check.py
|   |-- chain_load.py
|   |-- chain_verifiers.py
|   |-- ci_claims.py
|   |-- draft_publish_prediction.py
|   |-- emu_loop.py
|   |-- explore_run.py
|   |-- explore_step.py
|   |-- explore_text.py
|   |-- fragment_links.py
|   |-- measure_sample_predictors.py
|   |-- prediction_score.py
|   |-- region_shots.py
|   |-- smoke.py
|   |-- svg_legibility.py
|   |-- svg_text_gates.py
|   |-- test_blind_audit_targets.py
|   |-- test_chain.py
|   |-- test_draft_publish_prediction.py
|   |-- test_emu_loop.py
|   |-- test_explore_run.py
|   |-- test_explore_text.py
|   |-- test_external_svg.py
|   |-- test_fragment_links.py
|   |-- test_launch_sites.py
|   |-- test_prediction.py
|   `-- test_sync_artifact.py
|-- docs/
|   |-- claude-code-pkm/
|   |   |-- build/
|   |   |   |-- src/
|   |   |   |   |-- 01-sources-tags.txt
|   |   |   |   |-- 02-questions-decisions.txt
|   |   |   |   |-- 03-glossary-hook-events.txt
|   |   |   |   |-- 04-hook-rules-observations.txt
|   |   |   |   |-- 05-settings-permissions-memory.txt
|   |   |   |   |-- 06-tools-official.txt
|   |   |   |   |-- 07-tools-session.txt
|   |   |   |   |-- 08-tools-connectors.txt
|   |   |   |   |-- 09-skills.txt
|   |   |   |   |-- 10-commands-cli.txt
|   |   |   |   |-- 11-flags.txt
|   |   |   |   |-- 12-env-plugin-mcp-feature-agent.txt
|   |   |   |   |-- 13-process-git-injected-environment-gap.txt
|   |   |   |   |-- 14-method-and-snapshot.txt
|   |   |   |   |-- 15-settings-reference-a.txt
|   |   |   |   |-- 16-settings-reference-b.txt
|   |   |   |   |-- 17-settings-reference-c.txt
|   |   |   |   `-- 18-settings-reference-d.txt
|   |   |   `-- build_nodes.py
|   |   |-- nodes/
|   |   |   |-- agent-type.claude-code-guide.md
|   |   |   |-- agent-type.claude.md
|   |   |   |-- agent-type.explore.md
|   |   |   |-- agent-type.general-purpose.md
|   |   |   |-- agent-type.plan.md
|   |   |   |-- agent-type.statusline-setup.md
|   |   |   |-- agent-type.zapier-specialist.md
|   |   |   |-- cli-form.continue-print.md
|   |   |   |-- cli-form.continue.md
|   |   |   |-- cli-form.initial-prompt.md
|   |   |   |-- cli-form.interactive.md
|   |   |   |-- cli-form.pipe.md
|   |   |   |-- cli-form.print.md
|   |   |   |-- cli-form.resume.md
|   |   |   |-- cli.agents.md
|   |   |   |-- cli.attach.md
|   |   |   |-- cli.auth-login.md
|   |   |   |-- cli.auth-logout.md
|   |   |   |-- cli.auth-status.md
|   |   |   |-- cli.auto-mode-defaults.md
|   |   |   |-- cli.auto-mode-reset.md
|   |   |   |-- cli.daemon-logs.md
|   |   |   |-- cli.daemon-run.md
|   |   |   |-- cli.daemon-status.md
|   |   |   |-- cli.daemon-stop.md
|   |   |   |-- cli.doctor.md
|   |   |   |-- cli.gateway.md
|   |   |   |-- cli.import.md
|   |   |   |-- cli.install.md
|   |   |   |-- cli.logs.md
|   |   |   |-- cli.mcp-login.md
|   |   |   |-- cli.mcp-logout.md
|   |   |   |-- cli.mcp.md
|   |   |   |-- cli.plugin.md
|   |   |   |-- cli.purge.md
|   |   |   |-- cli.remote-control.md
|   |   |   |-- cli.respawn.md
|   |   |   |-- cli.rm.md
|   |   |   |-- cli.self-hosted-runner.md
|   |   |   |-- cli.setup-token.md
|   |   |   |-- cli.stop.md
|   |   |   |-- cli.ultrareview.md
|   |   |   |-- cli.update.md
|   |   |   |-- cmd.add-dir.md
|   |   |   |-- cmd.autocompact.md
|   |   |   |-- cmd.autofix-pr.md
|   |   |   |-- cmd.batch.md
|   |   |   |-- cmd.cd.md
|   |   |   |-- cmd.checkup.md
|   |   |   |-- cmd.claude-api.md
|   |   |   |-- cmd.clear.md
|   |   |   |-- cmd.code-review.md
|   |   |   |-- cmd.compact.md
|   |   |   |-- cmd.config.md
|   |   |   |-- cmd.context.md
|   |   |   |-- cmd.cost.md
|   |   |   |-- cmd.debug.md
|   |   |   |-- cmd.design.md
|   |   |   |-- cmd.diff.md
|   |   |   |-- cmd.doctor.md
|   |   |   |-- cmd.effort.md
|   |   |   |-- cmd.fast.md
|   |   |   |-- cmd.feedback.md
|   |   |   |-- cmd.goal.md
|   |   |   |-- cmd.help.md
|   |   |   |-- cmd.init.md
|   |   |   |-- cmd.list-agents.md
|   |   |   |-- cmd.login.md
|   |   |   |-- cmd.loop.md
|   |   |   |-- cmd.model.md
|   |   |   |-- cmd.permissions.md
|   |   |   |-- cmd.plugin.md
|   |   |   |-- cmd.radio.md
|   |   |   |-- cmd.reload-plugins.md
|   |   |   |-- cmd.reload-skills.md
|   |   |   |-- cmd.review.md
|   |   |   |-- cmd.rewind.md
|   |   |   |-- cmd.run-skill-generator.md
|   |   |   |-- cmd.run.md
|   |   |   |-- cmd.schedule.md
|   |   |   |-- cmd.security-review.md
|   |   |   |-- cmd.simplify.md
|   |   |   |-- cmd.skill-doctor.md
|   |   |   |-- cmd.skills.md
|   |   |   |-- cmd.status.md
|   |   |   |-- cmd.tasks.md
|   |   |   |-- cmd.team-onboarding.md
|   |   |   |-- cmd.ultrareview.md
|   |   |   |-- cmd.usage.md
|   |   |   |-- cmd.verify.md
|   |   |   |-- cmd.workflow-authoring.md
|   |   |   |-- dec.d1.md
|   |   |   |-- dec.d10.md
|   |   |   |-- dec.d11.md
|   |   |   |-- dec.d2.md
|   |   |   |-- dec.d3.md
|   |   |   |-- dec.d4.md
|   |   |   |-- dec.d5.md
|   |   |   |-- dec.d6.md
|   |   |   |-- dec.d7.md
|   |   |   |-- dec.d8.md
|   |   |   |-- dec.d9.md
|   |   |   |-- env.anthropic-model.md
|   |   |   |-- env.bash-default-timeout-ms.md
|   |   |   |-- env.bash-max-output-length.md
|   |   |   |-- env.bash-max-timeout-ms.md
|   |   |   |-- env.claude-ax-screen-reader.md
|   |   |   |-- env.claude-bash-maintain-project-working-dir.md
|   |   |   |-- env.claude-code-bridge-session-id.md
|   |   |   |-- env.claude-code-disable-background-tasks.md
|   |   |   |-- env.claude-code-disable-nonessential-traffic.md
|   |   |   |-- env.claude-code-enable-tasks.md
|   |   |   |-- env.claude-code-glob-no-ignore.md
|   |   |   |-- env.claude-code-powershell-respect-execution-policy.md
|   |   |   |-- env.claude-code-provider-managed-by-host.md
|   |   |   |-- env.claude-code-remote.md
|   |   |   |-- env.claude-code-safe-mode.md
|   |   |   |-- env.claude-code-simple.md
|   |   |   |-- env.claude-code-skip-prompt-history.md
|   |   |   |-- env.claude-code-subprocess-env-scrub.md
|   |   |   |-- env.claude-code-tool-memory-cgroup-exclude.md
|   |   |   |-- env.claude-code-tool-memory-limit.md
|   |   |   |-- env.claude-code-use-powershell-tool.md
|   |   |   |-- env.claude-config-dir.md
|   |   |   |-- env.claude-effort.md
|   |   |   |-- env.claude-env-file.md
|   |   |   |-- env.claude-plugin-data.md
|   |   |   |-- env.claude-plugin-option.md
|   |   |   |-- env.claude-plugin-root.md
|   |   |   |-- env.claude-project-dir.md
|   |   |   |-- env.claude-remote-control-session-name-prefix.md
|   |   |   |-- env.disable-telemetry.md
|   |   |   |-- env.mcp-timeout.md
|   |   |   |-- environment.claude-ai-chat.md
|   |   |   |-- environment.claude-ai-project-chat.md
|   |   |   |-- environment.claude-code-cloud.md
|   |   |   |-- environment.this-session.md
|   |   |   |-- feature.accessibility.md
|   |   |   |-- feature.advisor.md
|   |   |   |-- feature.agent-sdk.md
|   |   |   |-- feature.agent-teams.md
|   |   |   |-- feature.agent-view.md
|   |   |   |-- feature.analytics.md
|   |   |   |-- feature.auto-mode.md
|   |   |   |-- feature.changelog.md
|   |   |   |-- feature.channels.md
|   |   |   |-- feature.checkpointing.md
|   |   |   |-- feature.chrome.md
|   |   |   |-- feature.claude-code-on-the-web.md
|   |   |   |-- feature.claude-security.md
|   |   |   |-- feature.claude-tag.md
|   |   |   |-- feature.cloud-environments.md
|   |   |   |-- feature.code-review-prs.md
|   |   |   |-- feature.computer-use-cli.md
|   |   |   |-- feature.context-window.md
|   |   |   |-- feature.costs.md
|   |   |   |-- feature.cross-session-messaging.md
|   |   |   |-- feature.deep-links.md
|   |   |   |-- feature.desktop-app.md
|   |   |   |-- feature.fast-mode.md
|   |   |   |-- feature.fullscreen.md
|   |   |   |-- feature.github-actions.md
|   |   |   |-- feature.gitlab-ci-cd.md
|   |   |   |-- feature.goal.md
|   |   |   |-- feature.jetbrains.md
|   |   |   |-- feature.keybindings.md
|   |   |   |-- feature.local-code-review.md
|   |   |   |-- feature.mobile.md
|   |   |   |-- feature.model-config.md
|   |   |   |-- feature.monitoring.md
|   |   |   |-- feature.output-styles.md
|   |   |   |-- feature.print-mode.md
|   |   |   |-- feature.prompt-caching.md
|   |   |   |-- feature.remote-control.md
|   |   |   |-- feature.routines.md
|   |   |   |-- feature.sandbox-environments.md
|   |   |   |-- feature.sandboxing.md
|   |   |   |-- feature.scheduled-tasks.md
|   |   |   |-- feature.security-guidance.md
|   |   |   |-- feature.self-hosted-environments.md
|   |   |   |-- feature.session-management.md
|   |   |   |-- feature.slack.md
|   |   |   |-- feature.status-line.md
|   |   |   |-- feature.terminal-config.md
|   |   |   |-- feature.ultrareview.md
|   |   |   |-- feature.voice-dictation.md
|   |   |   |-- feature.vs-code.md
|   |   |   |-- feature.web-quickstart.md
|   |   |   |-- feature.whats-new.md
|   |   |   |-- feature.workflows.md
|   |   |   |-- feature.worktrees.md
|   |   |   |-- flag.add-dir.md
|   |   |   |-- flag.advisor.md
|   |   |   |-- flag.agent.md
|   |   |   |-- flag.agents.md
|   |   |   |-- flag.allow-dangerously-skip-permissions.md
|   |   |   |-- flag.allowed-tools.md
|   |   |   |-- flag.append-subagent-system-prompt-file.md
|   |   |   |-- flag.append-subagent-system-prompt.md
|   |   |   |-- flag.append-system-prompt-file.md
|   |   |   |-- flag.append-system-prompt.md
|   |   |   |-- flag.autocompact.md
|   |   |   |-- flag.ax-screen-reader.md
|   |   |   |-- flag.bare.md
|   |   |   |-- flag.betas.md
|   |   |   |-- flag.bg.md
|   |   |   |-- flag.channels.md
|   |   |   |-- flag.chrome.md
|   |   |   |-- flag.cloud.md
|   |   |   |-- flag.continue.md
|   |   |   |-- flag.dangerously-load-development-channels.md
|   |   |   |-- flag.dangerously-skip-permissions.md
|   |   |   |-- flag.debug-file.md
|   |   |   |-- flag.debug.md
|   |   |   |-- flag.desktop.md
|   |   |   |-- flag.disable-slash-commands.md
|   |   |   |-- flag.disallowed-tools.md
|   |   |   |-- flag.effort.md
|   |   |   |-- flag.enable-auto-mode.md
|   |   |   |-- flag.environment.md
|   |   |   |-- flag.exclude-dynamic-system-prompt-sections.md
|   |   |   |-- flag.exec.md
|   |   |   |-- flag.fallback-model.md
|   |   |   |-- flag.fork-session.md
|   |   |   |-- flag.forward-subagent-text.md
|   |   |   |-- flag.from-pr.md
|   |   |   |-- flag.ide.md
|   |   |   |-- flag.include-hook-events.md
|   |   |   |-- flag.include-partial-messages.md
|   |   |   |-- flag.init-only.md
|   |   |   |-- flag.init.md
|   |   |   |-- flag.input-format.md
|   |   |   |-- flag.json-schema.md
|   |   |   |-- flag.maintenance.md
|   |   |   |-- flag.max-budget-usd.md
|   |   |   |-- flag.max-turns.md
|   |   |   |-- flag.mcp-config.md
|   |   |   |-- flag.model.md
|   |   |   |-- flag.name.md
|   |   |   |-- flag.no-chrome.md
|   |   |   |-- flag.no-session-persistence.md
|   |   |   |-- flag.output-format.md
|   |   |   |-- flag.permission-mode.md
|   |   |   |-- flag.permission-prompt-tool.md
|   |   |   |-- flag.permission-prompts.md
|   |   |   |-- flag.plugin-dir.md
|   |   |   |-- flag.plugin-url.md
|   |   |   |-- flag.print.md
|   |   |   |-- flag.prompt-suggestions.md
|   |   |   |-- flag.ref.md
|   |   |   |-- flag.remote-control-session-name-prefix.md
|   |   |   |-- flag.remote-control.md
|   |   |   |-- flag.remote.md
|   |   |   |-- flag.replay-user-messages.md
|   |   |   |-- flag.restricted.md
|   |   |   |-- flag.resume.md
|   |   |   |-- flag.safe-mode.md
|   |   |   |-- flag.session-id.md
|   |   |   |-- flag.setting-sources.md
|   |   |   |-- flag.settings.md
|   |   |   |-- flag.strict-mcp-config.md
|   |   |   |-- flag.system-prompt-file.md
|   |   |   |-- flag.system-prompt-snapshot.md
|   |   |   |-- flag.system-prompt.md
|   |   |   |-- flag.teammate-mode.md
|   |   |   |-- flag.teleport.md
|   |   |   |-- flag.tmux.md
|   |   |   |-- flag.tools.md
|   |   |   |-- flag.verbose.md
|   |   |   |-- flag.version.md
|   |   |   |-- flag.worktree.md
|   |   |   |-- gap.commands-page.md
|   |   |   |-- gap.connector-schemas.md
|   |   |   |-- gap.env-vars-page.md
|   |   |   |-- gap.harness-pages-not-fetched.md
|   |   |   |-- gap.hook-stdin-schemas.md
|   |   |   |-- gap.keybindings.md
|   |   |   |-- gap.mcp-page.md
|   |   |   |-- gap.memory-page.md
|   |   |   |-- gap.plugin-mod-pages.md
|   |   |   |-- gap.sandbox-and-permission-pages.md
|   |   |   |-- gap.skill-bodies.md
|   |   |   |-- gap.subagents-page.md
|   |   |   |-- gap.tools-ref-tail.md
|   |   |   |-- git-rule.attribution.md
|   |   |   |-- git-rule.designated-branch.md
|   |   |   |-- git-rule.env-docs.md
|   |   |   |-- git-rule.no-history-rewrite.md
|   |   |   |-- git-rule.no-model-identifiers.md
|   |   |   |-- git-rule.open-pr-after-push.md
|   |   |   |-- git-rule.outputs-default.md
|   |   |   |-- git-rule.push-delete-noop.md
|   |   |   |-- git-rule.push-retry.md
|   |   |   |-- git-rule.subscribe-pr.md
|   |   |   |-- git-rule.template-check.md
|   |   |   |-- git-rule.tree-index-ci.md
|   |   |   |-- hook-rule.exit-0.md
|   |   |   |-- hook-rule.exit-2-blocks.md
|   |   |   |-- hook-rule.exit-2-non-blocking.md
|   |   |   |-- hook-rule.exit-other.md
|   |   |   |-- hook-rule.handler-agent.md
|   |   |   |-- hook-rule.handler-command.md
|   |   |   |-- hook-rule.handler-http.md
|   |   |   |-- hook-rule.handler-mcp-tool.md
|   |   |   |-- hook-rule.handler-prompt.md
|   |   |   |-- hook-rule.hook-specific-output-requires-event-name.md
|   |   |   |-- hook-rule.if-field.md
|   |   |   |-- hook-rule.levels.md
|   |   |   |-- hook-rule.location-local-settings.md
|   |   |   |-- hook-rule.location-managed-policy.md
|   |   |   |-- hook-rule.location-plugin.md
|   |   |   |-- hook-rule.location-project-settings.md
|   |   |   |-- hook-rule.location-skill-frontmatter.md
|   |   |   |-- hook-rule.location-subagent-frontmatter.md
|   |   |   |-- hook-rule.location-user-settings.md
|   |   |   |-- hook-rule.matcher-empty.md
|   |   |   |-- hook-rule.matcher-exact-or-list.md
|   |   |   |-- hook-rule.matcher-mcp-naming.md
|   |   |   |-- hook-rule.matcher-plugin-mcp-naming.md
|   |   |   |-- hook-rule.matcher-regex.md
|   |   |   |-- hook-rule.on-failure.md
|   |   |   |-- hook-rule.once.md
|   |   |   |-- hook-rule.output-permission-request.md
|   |   |   |-- hook-rule.output-pre-tool-use.md
|   |   |   |-- hook-rule.output-session-start.md
|   |   |   |-- hook-rule.output-size-cap.md
|   |   |   |-- hook-rule.output-top-level-block.md
|   |   |   |-- hook-rule.output-universal.md
|   |   |   |-- hook-rule.stdin-common-fields.md
|   |   |   |-- hook-rule.stdin-model-switch.md
|   |   |   |-- hook-rule.stdin-notification.md
|   |   |   |-- hook-rule.stdin-pre-tool-use.md
|   |   |   |-- hook-rule.stdin-session-start.md
|   |   |   |-- hook-rule.stdin-stop.md
|   |   |   |-- hook-rule.timeout-defaults.md
|   |   |   |-- hook-rule.timeouts.md
|   |   |   |-- hook.config-change.md
|   |   |   |-- hook.cwd-changed.md
|   |   |   |-- hook.directory-added.md
|   |   |   |-- hook.elicitation-result.md
|   |   |   |-- hook.elicitation.md
|   |   |   |-- hook.file-changed.md
|   |   |   |-- hook.instructions-loaded.md
|   |   |   |-- hook.message-display.md
|   |   |   |-- hook.notification.md
|   |   |   |-- hook.permission-denied.md
|   |   |   |-- hook.permission-request.md
|   |   |   |-- hook.post-compact.md
|   |   |   |-- hook.post-model-switch.md
|   |   |   |-- hook.post-tool-batch.md
|   |   |   |-- hook.post-tool-use-failure.md
|   |   |   |-- hook.post-tool-use.md
|   |   |   |-- hook.pre-compact.md
|   |   |   |-- hook.pre-model-switch.md
|   |   |   |-- hook.pre-tool-use.md
|   |   |   |-- hook.session-end.md
|   |   |   |-- hook.session-start.md
|   |   |   |-- hook.setup.md
|   |   |   |-- hook.stop-failure.md
|   |   |   |-- hook.stop.md
|   |   |   |-- hook.subagent-start.md
|   |   |   |-- hook.subagent-stop.md
|   |   |   |-- hook.task-completed.md
|   |   |   |-- hook.task-created.md
|   |   |   |-- hook.teammate-idle.md
|   |   |   |-- hook.user-prompt-expansion.md
|   |   |   |-- hook.user-prompt-submit.md
|   |   |   |-- hook.worktree-create.md
|   |   |   |-- hook.worktree-remove.md
|   |   |   |-- injected.account-context.md
|   |   |   |-- injected.attribution-reminder.md
|   |   |   |-- injected.claude-md-reminder.md
|   |   |   |-- injected.event-envelopes.md
|   |   |   |-- injected.lists.md
|   |   |   |-- injected.model-notices.md
|   |   |   |-- injected.pasted-content.md
|   |   |   |-- injected.server-notices.md
|   |   |   |-- injected.system-turns.md
|   |   |   |-- injected.task-notification.md
|   |   |   |-- injected.tool-listing-snapshot.md
|   |   |   |-- injected.tool-result-data.md
|   |   |   |-- injected.total-tokens.md
|   |   |   |-- mcp.channels.md
|   |   |   |-- mcp.connectors-and-plugin-servers.md
|   |   |   |-- mcp.managed.md
|   |   |   |-- mcp.naming.md
|   |   |   |-- mcp.overview.md
|   |   |   |-- mcp.resources.md
|   |   |   |-- mcp.tool-search.md
|   |   |   |-- memory.agents-md.md
|   |   |   |-- memory.auto-memory.md
|   |   |   |-- memory.claude-md.md
|   |   |   |-- memory.connector-memory.md
|   |   |   |-- memory.dynamic-prompt-sections.md
|   |   |   |-- memory.import-syntax.md
|   |   |   |-- memory.lazy-load-by-view.md
|   |   |   |-- memory.load-reason-compact.md
|   |   |   |-- memory.load-reason-include.md
|   |   |   |-- memory.load-reason-nested-traversal.md
|   |   |   |-- memory.load-reason-path-glob-match.md
|   |   |   |-- memory.load-reason-session-start.md
|   |   |   |-- memory.rules-dir.md
|   |   |   |-- mod.admin.md
|   |   |   |-- mod.hooks-module.md
|   |   |   |-- mod.overview.md
|   |   |   |-- mod.panes.md
|   |   |   |-- mod.tool-call-rules.md
|   |   |   |-- obs.claude-project-dir-unset-in-bash.md
|   |   |   |-- obs.clone-remote-no-credential.md
|   |   |   |-- obs.git-proxy-push-delete-noop.md
|   |   |   |-- obs.hook-mid-session-no-effect.md
|   |   |   |-- obs.hook-overhead-55ms.md
|   |   |   |-- obs.repo-session-start-hook.md
|   |   |   |-- obs.session-start-banner-not-visible.md
|   |   |   |-- obs.user-stop-hook-feedback.md
|   |   |   |-- permission-mode.accept-edits.md
|   |   |   |-- permission-mode.auto.md
|   |   |   |-- permission-mode.bypass-permissions.md
|   |   |   |-- permission-mode.default.md
|   |   |   |-- permission-mode.dont-ask.md
|   |   |   |-- permission-mode.manual.md
|   |   |   |-- permission-mode.plan.md
|   |   |   |-- permission-rule.allow-ask-deny-lists.md
|   |   |   |-- permission-rule.bash-deny-disables-powershell.md
|   |   |   |-- permission-rule.edit-grants-read.md
|   |   |   |-- permission-rule.form.md
|   |   |   |-- permission-rule.managed-allow-merge.md
|   |   |   |-- permission-rule.no-specifier-tools.md
|   |   |   |-- permission-rule.project-trust.md
|   |   |   |-- permission-rule.read-deny-blocks-edit.md
|   |   |   |-- permission-rule.saved-approval-local-file.md
|   |   |   |-- permission-rule.specifier-agent.md
|   |   |   |-- permission-rule.specifier-bash.md
|   |   |   |-- permission-rule.specifier-powershell.md
|   |   |   |-- permission-rule.specifier-read-edit.md
|   |   |   |-- permission-rule.specifier-skill.md
|   |   |   |-- permission-rule.specifier-webfetch.md
|   |   |   |-- permission-rule.specifier-websearch.md
|   |   |   |-- plugin.commands-cli.md
|   |   |   |-- plugin.components.md
|   |   |   |-- plugin.dependencies.md
|   |   |   |-- plugin.evals.md
|   |   |   |-- plugin.hooks-json.md
|   |   |   |-- plugin.install.md
|   |   |   |-- plugin.load-flags.md
|   |   |   |-- plugin.loading.md
|   |   |   |-- plugin.marketplaces.md
|   |   |   |-- plugin.org-management.md
|   |   |   |-- plugin.overview.md
|   |   |   |-- plugin.security.md
|   |   |   |-- precedence.command-line.md
|   |   |   |-- precedence.env-not-a-level.md
|   |   |   |-- precedence.lists-merge.md
|   |   |   |-- precedence.managed-exceptions.md
|   |   |   |-- precedence.managed.md
|   |   |   |-- precedence.project-local.md
|   |   |   |-- precedence.rule.md
|   |   |   |-- precedence.shared-project.md
|   |   |   |-- precedence.user.md
|   |   |   |-- process.ask-user-question-timeout.md
|   |   |   |-- process.background-stop-rules.md
|   |   |   |-- process.background-time-limit.md
|   |   |   |-- process.bash-cd-persistence.md
|   |   |   |-- process.bash-env-persistence.md
|   |   |   |-- process.bash-output-limits.md
|   |   |   |-- process.build.md
|   |   |   |-- process.conflict-rule.md
|   |   |   |-- process.foreground-to-background.md
|   |   |   |-- process.loop-pacing.md
|   |   |   |-- process.memory-cap.md
|   |   |   |-- process.monitor-deadline.md
|   |   |   |-- process.session-cron-expiry.md
|   |   |   |-- process.subagent-permission-routing.md
|   |   |   |-- question.q1.md
|   |   |   |-- question.q10.md
|   |   |   |-- question.q11.md
|   |   |   |-- question.q12.md
|   |   |   |-- question.q13.md
|   |   |   |-- question.q14.md
|   |   |   |-- question.q15.md
|   |   |   |-- question.q2.md
|   |   |   |-- question.q3.md
|   |   |   |-- question.q4.md
|   |   |   |-- question.q5.md
|   |   |   |-- question.q6.md
|   |   |   |-- question.q7.md
|   |   |   |-- question.q8.md
|   |   |   |-- question.q9.md
|   |   |   |-- session-rule.adhd-formatting.md
|   |   |   |-- session-rule.inline-source-links.md
|   |   |   |-- session-rule.no-spawns-or-task-lists.md
|   |   |   |-- session-rule.tool-budget.md
|   |   |   |-- setting-file.global-config.md
|   |   |   |-- setting-file.managed.md
|   |   |   |-- setting-file.project-local.md
|   |   |   |-- setting-file.shared-project.md
|   |   |   |-- setting-file.user.md
|   |   |   |-- setting.advisor-model.md
|   |   |   |-- setting.agent-push-notif-enabled.md
|   |   |   |-- setting.agent.md
|   |   |   |-- setting.allow-all-claude-ai-mcps.md
|   |   |   |-- setting.allow-claude-in-chrome-with-managed-mcp.md
|   |   |   |-- setting.allow-managed-hooks-only.md
|   |   |   |-- setting.allow-managed-mcp-servers-only.md
|   |   |   |-- setting.allow-managed-permission-rules-only.md
|   |   |   |-- setting.allowed-channel-plugins.md
|   |   |   |-- setting.allowed-http-hook-urls.md
|   |   |   |-- setting.allowed-mcp-servers.md
|   |   |   |-- setting.allowed-providers.md
|   |   |   |-- setting.always-thinking-enabled.md
|   |   |   |-- setting.api-key-helper.md
|   |   |   |-- setting.append-plugins.md
|   |   |   |-- setting.ask-user-question-timeout.md
|   |   |   |-- setting.attribution-commit.md
|   |   |   |-- setting.attribution-pr.md
|   |   |   |-- setting.attribution-session-url.md
|   |   |   |-- setting.attribution.md
|   |   |   |-- setting.auto-compact-enabled.md
|   |   |   |-- setting.auto-compact-window.md
|   |   |   |-- setting.auto-connect-ide.md
|   |   |   |-- setting.auto-continue-at-usage-limit.md
|   |   |   |-- setting.auto-install-ide-extension.md
|   |   |   |-- setting.auto-memory-directory.md
|   |   |   |-- setting.auto-memory-enabled.md
|   |   |   |-- setting.auto-mode-classify-all-shell.md
|   |   |   |-- setting.auto-mode.md
|   |   |   |-- setting.auto-scroll-enabled.md
|   |   |   |-- setting.auto-updates-channel.md
|   |   |   |-- setting.available-models-match.md
|   |   |   |-- setting.available-models.md
|   |   |   |-- setting.away-summary-enabled.md
|   |   |   |-- setting.aws-auth-refresh.md
|   |   |   |-- setting.aws-credential-export.md
|   |   |   |-- setting.ax-screen-reader.md
|   |   |   |-- setting.bash-edit-diff-enabled.md
|   |   |   |-- setting.bash-output-max-chars.md
|   |   |   |-- setting.blocked-marketplaces.md
|   |   |   |-- setting.broken-entry-warning.md
|   |   |   |-- setting.broken-json-error.md
|   |   |   |-- setting.browser-external-page-tools.md
|   |   |   |-- setting.channels-enabled.md
|   |   |   |-- setting.claude-in-chrome-default-enabled.md
|   |   |   |-- setting.claude-md-excludes.md
|   |   |   |-- setting.claude-md.md
|   |   |   |-- setting.cleanup-period-days.md
|   |   |   |-- setting.cloud-device-managed-not-read.md
|   |   |   |-- setting.cloud-repo-file-read.md
|   |   |   |-- setting.cloud-user-local-not-read.md
|   |   |   |-- setting.company-announcements.md
|   |   |   |-- setting.copy-full-response.md
|   |   |   |-- setting.copy-on-select.md
|   |   |   |-- setting.cross-session-inbound.md
|   |   |   |-- setting.default-shell.md
|   |   |   |-- setting.default-to-agents-view.md
|   |   |   |-- setting.denied-mcp-servers.md
|   |   |   |-- setting.denied-models.md
|   |   |   |-- setting.desktop-session-cleanup-period-days.md
|   |   |   |-- setting.dialog-expiry.md
|   |   |   |-- setting.diff-tool.md
|   |   |   |-- setting.disable-agent-view.md
|   |   |   |-- setting.disable-all-hooks.md
|   |   |   |-- setting.disable-artifact.md
|   |   |   |-- setting.disable-auto-mode.md
|   |   |   |-- setting.disable-browser-external-navigation.md
|   |   |   |-- setting.disable-bundled-skills.md
|   |   |   |-- setting.disable-claude-ai-connectors.md
|   |   |   |-- setting.disable-command-plugin-sources.md
|   |   |   |-- setting.disable-deep-link-registration.md
|   |   |   |-- setting.disable-desktop-local-sessions.md
|   |   |   |-- setting.disable-mobile-simulator-tools.md
|   |   |   |-- setting.disable-remote-control.md
|   |   |   |-- setting.disable-sideload-flags.md
|   |   |   |-- setting.disable-skill-shell-execution.md
|   |   |   |-- setting.disable-workflows.md
|   |   |   |-- setting.disabled-mcpjson-servers.md
|   |   |   |-- setting.editor-mode.md
|   |   |   |-- setting.effort-level.md
|   |   |   |-- setting.emoji-completion-enabled.md
|   |   |   |-- setting.enable-all-project-mcp-servers.md
|   |   |   |-- setting.enable-artifact.md
|   |   |   |-- setting.enable-workflows.md
|   |   |   |-- setting.enabled-mcpjson-servers.md
|   |   |   |-- setting.enabled-plugins.md
|   |   |   |-- setting.enforce-available-models.md
|   |   |   |-- setting.env.md
|   |   |   |-- setting.external-editor-context.md
|   |   |   |-- setting.extra-known-marketplaces.md
|   |   |   |-- setting.fallback-model.md
|   |   |   |-- setting.fast-mode-per-session-opt-in.md
|   |   |   |-- setting.fast-mode.md
|   |   |   |-- setting.feedback-drafts.md
|   |   |   |-- setting.feedback-survey-rate.md
|   |   |   |-- setting.file-checkpointing-enabled.md
|   |   |   |-- setting.file-suggestion.md
|   |   |   |-- setting.footer-links-regexes.md
|   |   |   |-- setting.force-login-gateway-url.md
|   |   |   |-- setting.force-login-method.md
|   |   |   |-- setting.force-login-org-uuid.md
|   |   |   |-- setting.force-remote-settings-refresh.md
|   |   |   |-- setting.gateway-internal-networks.md
|   |   |   |-- setting.gcp-auth-refresh.md
|   |   |   |-- setting.hooks.md
|   |   |   |-- setting.http-hook-allowed-env-vars.md
|   |   |   |-- setting.idle-compaction.md
|   |   |   |-- setting.include-co-authored-by.md
|   |   |   |-- setting.include-git-instructions.md
|   |   |   |-- setting.input-needed-notif-enabled.md
|   |   |   |-- setting.isolate-peer-machines.md
|   |   |   |-- setting.keybinding-flavor.md
|   |   |   |-- setting.kill-switch.allow-managed-hooks-only.md
|   |   |   |-- setting.kill-switch.allowed-http-hook-urls.md
|   |   |   |-- setting.kill-switch.disable-all-hooks.md
|   |   |   |-- setting.kill-switch.http-hook-allowed-env-vars.md
|   |   |   |-- setting.language.md
|   |   |   |-- setting.left-arrow-opens-agents.md
|   |   |   |-- setting.live-reload.md
|   |   |   |-- setting.managed-exception.block-reads-outside-working-directories.md
|   |   |   |-- setting.managed-exception.classify-all-shell.md
|   |   |   |-- setting.managed-exception.cross-session-inbound.md
|   |   |   |-- setting.managed-exception.disable-claude-ai-connectors.md
|   |   |   |-- setting.managed-exception.enable-artifact.md
|   |   |   |-- setting.managed-exception.isolate-peer-machines.md
|   |   |   |-- setting.managed-exception.max-effort-level.md
|   |   |   |-- setting.managed-exception.remote-control-at-startup.md
|   |   |   |-- setting.managed-exception.sync-claude-ai-plugins.md
|   |   |   |-- setting.managed-exception.sync-claude-ai-skills.md
|   |   |   |-- setting.managed-exception.use-auto-mode-during-plan.md
|   |   |   |-- setting.managed-invalid-entries.md
|   |   |   |-- setting.managed-mcp-servers.md
|   |   |   |-- setting.managed-sources-behavior.md
|   |   |   |-- setting.max-effort-level.md
|   |   |   |-- setting.max-prose-width.md
|   |   |   |-- setting.minimum-version.md
|   |   |   |-- setting.model-overrides.md
|   |   |   |-- setting.model-picker.md
|   |   |   |-- setting.model-pricing.md
|   |   |   |-- setting.model.md
|   |   |   |-- setting.otel-headers-helper.md
|   |   |   |-- setting.output-style.md
|   |   |   |-- setting.parent-settings-behavior.md
|   |   |   |-- setting.permission-explainer-enabled.md
|   |   |   |-- setting.permissions-additional-directories.md
|   |   |   |-- setting.permissions-allow.md
|   |   |   |-- setting.permissions-ask.md
|   |   |   |-- setting.permissions-block-reads-outside-working-directories.md
|   |   |   |-- setting.permissions-default-mode-limit.md
|   |   |   |-- setting.permissions-default-mode.md
|   |   |   |-- setting.permissions-deny.md
|   |   |   |-- setting.permissions-disable-bypass-permissions-mode.md
|   |   |   |-- setting.permissions.md
|   |   |   |-- setting.plans-directory.md
|   |   |   |-- setting.plugin-configs.md
|   |   |   |-- setting.plugin-suggestion-marketplaces.md
|   |   |   |-- setting.plugin-trust-message.md
|   |   |   |-- setting.policy-helper-path.md
|   |   |   |-- setting.policy-helper-refresh-interval-ms.md
|   |   |   |-- setting.policy-helper-timeout-ms.md
|   |   |   |-- setting.policy-helper.md
|   |   |   |-- setting.pr-status-footer-enabled.md
|   |   |   |-- setting.pr-url-template.md
|   |   |   |-- setting.preferred-notif-channel.md
|   |   |   |-- setting.prefers-reduced-motion.md
|   |   |   |-- setting.prepend-plugins.md
|   |   |   |-- setting.print-mode-broken-file.md
|   |   |   |-- setting.process-wrapper.md
|   |   |   |-- setting.prompt-cache-ttl.md
|   |   |   |-- setting.prompt-suggestion-enabled.md
|   |   |   |-- setting.remote-control-at-startup.md
|   |   |   |-- setting.remote-default-environment-id.md
|   |   |   |-- setting.required-maximum-version.md
|   |   |   |-- setting.required-minimum-version.md
|   |   |   |-- setting.respect-gitignore.md
|   |   |   |-- setting.respond-to-bash-commands.md
|   |   |   |-- setting.sandbox-allow-apple-events.md
|   |   |   |-- setting.sandbox-allow-unsandboxed-commands.md
|   |   |   |-- setting.sandbox-auto-allow-bash-if-sandboxed.md
|   |   |   |-- setting.sandbox-bwrap-path.md
|   |   |   |-- setting.sandbox-credentials-allow-plaintext-inject.md
|   |   |   |-- setting.sandbox-credentials-aws-pairs.md
|   |   |   |-- setting.sandbox-credentials-env-vars.md
|   |   |   |-- setting.sandbox-credentials-files.md
|   |   |   |-- setting.sandbox-credentials-sigv4.md
|   |   |   |-- setting.sandbox-credentials.md
|   |   |   |-- setting.sandbox-enable-weaker-nested-sandbox.md
|   |   |   |-- setting.sandbox-enable-weaker-network-isolation.md
|   |   |   |-- setting.sandbox-enabled.md
|   |   |   |-- setting.sandbox-excluded-commands.md
|   |   |   |-- setting.sandbox-fail-if-unavailable.md
|   |   |   |-- setting.sandbox-filesystem-allow-managed-read-paths-only.md
|   |   |   |-- setting.sandbox-filesystem-allow-read.md
|   |   |   |-- setting.sandbox-filesystem-allow-write.md
|   |   |   |-- setting.sandbox-filesystem-deny-read.md
|   |   |   |-- setting.sandbox-filesystem-deny-write.md
|   |   |   |-- setting.sandbox-filesystem-disabled.md
|   |   |   |-- setting.sandbox-filesystem.md
|   |   |   |-- setting.sandbox-ignore-violations.md
|   |   |   |-- setting.sandbox-network-allow-all-unix-sockets.md
|   |   |   |-- setting.sandbox-network-allow-local-binding.md
|   |   |   |-- setting.sandbox-network-allow-mach-lookup.md
|   |   |   |-- setting.sandbox-network-allow-managed-domains-only.md
|   |   |   |-- setting.sandbox-network-allow-unix-sockets.md
|   |   |   |-- setting.sandbox-network-allowed-domains.md
|   |   |   |-- setting.sandbox-network-denied-domains.md
|   |   |   |-- setting.sandbox-network-http-proxy-port.md
|   |   |   |-- setting.sandbox-network-socks-proxy-port.md
|   |   |   |-- setting.sandbox-network-strict-allowlist.md
|   |   |   |-- setting.sandbox-network-tls-terminate.md
|   |   |   |-- setting.sandbox-network.md
|   |   |   |-- setting.sandbox-ripgrep.md
|   |   |   |-- setting.sandbox-socat-path.md
|   |   |   |-- setting.sandbox.md
|   |   |   |-- setting.schema-url.md
|   |   |   |-- setting.show-clear-context-on-plan-accept.md
|   |   |   |-- setting.show-thinking-summaries.md
|   |   |   |-- setting.show-turn-duration.md
|   |   |   |-- setting.skill-listing-budget-fraction.md
|   |   |   |-- setting.skill-listing-max-desc-chars.md
|   |   |   |-- setting.skill-overrides.md
|   |   |   |-- setting.skip-auto-permission-prompt.md
|   |   |   |-- setting.skip-dangerous-mode-permission-prompt.md
|   |   |   |-- setting.skip-web-fetch-preflight.md
|   |   |   |-- setting.spellcheck.md
|   |   |   |-- setting.spinner-tips-enabled.md
|   |   |   |-- setting.spinner-tips-override.md
|   |   |   |-- setting.spinner-verbs.md
|   |   |   |-- setting.ssh-configs.md
|   |   |   |-- setting.ssh-host-allowlist.md
|   |   |   |-- setting.status-line.md
|   |   |   |-- setting.strict-known-marketplaces.md
|   |   |   |-- setting.strict-plugin-only-customization-agents.md
|   |   |   |-- setting.strict-plugin-only-customization-hooks.md
|   |   |   |-- setting.strict-plugin-only-customization-mcp.md
|   |   |   |-- setting.strict-plugin-only-customization-skills.md
|   |   |   |-- setting.strict-plugin-only-customization.md
|   |   |   |-- setting.subagent-prompt-cache-ttl.md
|   |   |   |-- setting.subagent-status-line.md
|   |   |   |-- setting.switch-models-on-flag.md
|   |   |   |-- setting.sync-claude-ai-plugins.md
|   |   |   |-- setting.sync-claude-ai-skills.md
|   |   |   |-- setting.syntax-highlighting-disabled.md
|   |   |   |-- setting.task-output-max-chars.md
|   |   |   |-- setting.teammate-default-model.md
|   |   |   |-- setting.teammate-mode.md
|   |   |   |-- setting.terminal-progress-bar-enabled.md
|   |   |   |-- setting.terminal-title-from-rename.md
|   |   |   |-- setting.theme.md
|   |   |   |-- setting.time-format.md
|   |   |   |-- setting.time-zone.md
|   |   |   |-- setting.tui.md
|   |   |   |-- setting.ultracode.md
|   |   |   |-- setting.use-auto-mode-during-plan.md
|   |   |   |-- setting.verbose.md
|   |   |   |-- setting.viewmode.md
|   |   |   |-- setting.vim-insert-mode-remaps.md
|   |   |   |-- setting.voice-enabled.md
|   |   |   |-- setting.voice.md
|   |   |   |-- setting.wheel-scroll-acceleration-enabled.md
|   |   |   |-- setting.workflow-keyword-trigger-enabled.md
|   |   |   |-- setting.workflow-size-guideline.md
|   |   |   |-- setting.worktree-base-ref.md
|   |   |   |-- setting.worktree-bg-isolation.md
|   |   |   |-- setting.worktree-location.md
|   |   |   |-- setting.worktree-sparse-paths.md
|   |   |   |-- setting.worktree-symlink-directories.md
|   |   |   |-- setting.worktree.md
|   |   |   |-- setting.wsl-inherits-windows-settings.md
|   |   |   |-- skill.anthropic-skills-algorithmic-art.md
|   |   |   |-- skill.anthropic-skills-brand-guidelines.md
|   |   |   |-- skill.anthropic-skills-built-in-browser.md
|   |   |   |-- skill.anthropic-skills-canvas-design.md
|   |   |   |-- skill.anthropic-skills-chrome-browser.md
|   |   |   |-- skill.anthropic-skills-computer-use.md
|   |   |   |-- skill.anthropic-skills-deep-research.md
|   |   |   |-- skill.anthropic-skills-dirtree.md
|   |   |   |-- skill.anthropic-skills-doc-coauthoring.md
|   |   |   |-- skill.anthropic-skills-docs.md
|   |   |   |-- skill.anthropic-skills-docx.md
|   |   |   |-- skill.anthropic-skills-google-workspace.md
|   |   |   |-- skill.anthropic-skills-import-memory.md
|   |   |   |-- skill.anthropic-skills-mcp-builder.md
|   |   |   |-- skill.anthropic-skills-morning.md
|   |   |   |-- skill.anthropic-skills-pdf.md
|   |   |   |-- skill.anthropic-skills-pptx.md
|   |   |   |-- skill.anthropic-skills-skill-creator.md
|   |   |   |-- skill.anthropic-skills-theme-factory.md
|   |   |   |-- skill.anthropic-skills-web-artifacts-builder.md
|   |   |   |-- skill.anthropic-skills-xlsx.md
|   |   |   |-- skill.artifact-capabilities.md
|   |   |   |-- skill.artifact-design.md
|   |   |   |-- skill.artifact-diagramming.md
|   |   |   |-- skill.claude-api.md
|   |   |   |-- skill.code-review.md
|   |   |   |-- skill.data-analyze.md
|   |   |   |-- skill.data-build-dashboard.md
|   |   |   |-- skill.data-context-extractor.md
|   |   |   |-- skill.data-create-viz.md
|   |   |   |-- skill.data-explore.md
|   |   |   |-- skill.data-sql-queries.md
|   |   |   |-- skill.data-statistical-analysis.md
|   |   |   |-- skill.data-validate-data.md
|   |   |   |-- skill.data-visualization.md
|   |   |   |-- skill.data-write-query.md
|   |   |   |-- skill.dataviz.md
|   |   |   |-- skill.design-accessibility-review.md
|   |   |   |-- skill.design-critique.md
|   |   |   |-- skill.design-handoff.md
|   |   |   |-- skill.design-research-synthesis.md
|   |   |   |-- skill.design-system.md
|   |   |   |-- skill.design-user-research.md
|   |   |   |-- skill.design-ux-copy.md
|   |   |   |-- skill.engineering-architecture.md
|   |   |   |-- skill.engineering-code-review.md
|   |   |   |-- skill.engineering-debug.md
|   |   |   |-- skill.engineering-deploy-checklist.md
|   |   |   |-- skill.engineering-documentation.md
|   |   |   |-- skill.engineering-incident-response.md
|   |   |   |-- skill.engineering-standup.md
|   |   |   |-- skill.engineering-system-design.md
|   |   |   |-- skill.engineering-tech-debt.md
|   |   |   |-- skill.engineering-testing-strategy.md
|   |   |   |-- skill.fewer-permission-prompts.md
|   |   |   |-- skill.init.md
|   |   |   |-- skill.keybindings-help.md
|   |   |   |-- skill.loop.md
|   |   |   |-- skill.pdf-viewer-annotate.md
|   |   |   |-- skill.pdf-viewer-fill-form.md
|   |   |   |-- skill.pdf-viewer-open.md
|   |   |   |-- skill.pdf-viewer-sign.md
|   |   |   |-- skill.pdf-viewer-view-pdf.md
|   |   |   |-- skill.plugin-authoring.md
|   |   |   |-- skill.productivity-memory-management.md
|   |   |   |-- skill.productivity-start.md
|   |   |   |-- skill.productivity-task-management.md
|   |   |   |-- skill.productivity-update.md
|   |   |   |-- skill.run.md
|   |   |   |-- skill.security-review.md
|   |   |   |-- skill.session-start-hook.md
|   |   |   |-- skill.simplify.md
|   |   |   |-- skill.update-config.md
|   |   |   |-- skill.workflow-authoring.md
|   |   |   |-- skill.zapier-demo.md
|   |   |   |-- skill.zapier-explore.md
|   |   |   |-- skill.zapier-onboard.md
|   |   |   |-- skill.zapier-status.md
|   |   |   |-- src.s1.md
|   |   |   |-- src.s10.md
|   |   |   |-- src.s11.md
|   |   |   |-- src.s12.md
|   |   |   |-- src.s13.md
|   |   |   |-- src.s2.md
|   |   |   |-- src.s3.md
|   |   |   |-- src.s4.md
|   |   |   |-- src.s5.md
|   |   |   |-- src.s6.md
|   |   |   |-- src.s7.md
|   |   |   |-- src.s8.md
|   |   |   |-- src.s9.md
|   |   |   |-- tag.gap.md
|   |   |   |-- tag.index.md
|   |   |   |-- tag.open.md
|   |   |   |-- tag.repo.md
|   |   |   |-- tag.session.md
|   |   |   |-- tag.unverified.md
|   |   |   |-- tag.verified.md
|   |   |   |-- term.artifact.md
|   |   |   |-- term.background-task.md
|   |   |   |-- term.built-in-tool.md
|   |   |   |-- term.compaction.md
|   |   |   |-- term.connector.md
|   |   |   |-- term.deferred-tool.md
|   |   |   |-- term.fork.md
|   |   |   |-- term.harness.md
|   |   |   |-- term.hook.md
|   |   |   |-- term.matcher.md
|   |   |   |-- term.mcp-server.md
|   |   |   |-- term.mod.md
|   |   |   |-- term.permission-column.md
|   |   |   |-- term.permission-mode.md
|   |   |   |-- term.permission-rule.md
|   |   |   |-- term.plugin.md
|   |   |   |-- term.remote-session.md
|   |   |   |-- term.settings-scope.md
|   |   |   |-- term.skill.md
|   |   |   |-- term.subagent.md
|   |   |   |-- term.teammate.md
|   |   |   |-- term.toolsearch.md
|   |   |   |-- term.workflow.md
|   |   |   |-- tool.agent.md
|   |   |   |-- tool.alphaxiv-answer-pdf-queries.md
|   |   |   |-- tool.alphaxiv-discover-papers.md
|   |   |   |-- tool.alphaxiv-get-for-you-feed.md
|   |   |   |-- tool.alphaxiv-get-hot-feed.md
|   |   |   |-- tool.alphaxiv-get-paper-content.md
|   |   |   |-- tool.alphaxiv-read-files-from-github-repository.md
|   |   |   |-- tool.artifact-comments.md
|   |   |   |-- tool.artifact-data.md
|   |   |   |-- tool.artifact.md
|   |   |   |-- tool.ask-user-question.md
|   |   |   |-- tool.bash.md
|   |   |   |-- tool.claude-docs-batch.md
|   |   |   |-- tool.claude-docs-create.md
|   |   |   |-- tool.claude-docs-delete.md
|   |   |   |-- tool.claude-docs-export.md
|   |   |   |-- tool.claude-docs-guide.md
|   |   |   |-- tool.claude-docs-query.md
|   |   |   |-- tool.claude-docs-read.md
|   |   |   |-- tool.claude-docs-update.md
|   |   |   |-- tool.cron-create.md
|   |   |   |-- tool.cron-delete.md
|   |   |   |-- tool.cron-list.md
|   |   |   |-- tool.design-sync.md
|   |   |   |-- tool.edit.md
|   |   |   |-- tool.end-conversation.md
|   |   |   |-- tool.enter-plan-mode.md
|   |   |   |-- tool.enter-worktree.md
|   |   |   |-- tool.exit-plan-mode.md
|   |   |   |-- tool.exit-worktree.md
|   |   |   |-- tool.github-actions-get.md
|   |   |   |-- tool.github-actions-list.md
|   |   |   |-- tool.github-actions-run-trigger.md
|   |   |   |-- tool.github-add-comment-to-pending-review.md
|   |   |   |-- tool.github-add-issue-comment.md
|   |   |   |-- tool.github-add-reply-to-pull-request-comment.md
|   |   |   |-- tool.github-assign-copilot-to-issue.md
|   |   |   |-- tool.github-create-branch.md
|   |   |   |-- tool.github-create-or-update-file.md
|   |   |   |-- tool.github-create-pull-request-with-copilot.md
|   |   |   |-- tool.github-create-pull-request.md
|   |   |   |-- tool.github-create-repository.md
|   |   |   |-- tool.github-delete-file.md
|   |   |   |-- tool.github-disable-pr-auto-merge.md
|   |   |   |-- tool.github-enable-pr-auto-merge.md
|   |   |   |-- tool.github-fork-repository.md
|   |   |   |-- tool.github-get-check-run.md
|   |   |   |-- tool.github-get-commit.md
|   |   |   |-- tool.github-get-copilot-job-status.md
|   |   |   |-- tool.github-get-file-contents.md
|   |   |   |-- tool.github-get-job-logs.md
|   |   |   |-- tool.github-get-label.md
|   |   |   |-- tool.github-get-latest-release.md
|   |   |   |-- tool.github-get-me.md
|   |   |   |-- tool.github-get-release-by-tag.md
|   |   |   |-- tool.github-get-tag.md
|   |   |   |-- tool.github-get-team-members.md
|   |   |   |-- tool.github-get-teams.md
|   |   |   |-- tool.github-issue-read.md
|   |   |   |-- tool.github-issue-write.md
|   |   |   |-- tool.github-list-branches.md
|   |   |   |-- tool.github-list-commits.md
|   |   |   |-- tool.github-list-issue-fields.md
|   |   |   |-- tool.github-list-issue-types.md
|   |   |   |-- tool.github-list-issues.md
|   |   |   |-- tool.github-list-pull-requests.md
|   |   |   |-- tool.github-list-releases.md
|   |   |   |-- tool.github-list-repository-collaborators.md
|   |   |   |-- tool.github-list-tags.md
|   |   |   |-- tool.github-merge-pull-request.md
|   |   |   |-- tool.github-pull-request-read.md
|   |   |   |-- tool.github-pull-request-review-write.md
|   |   |   |-- tool.github-push-files.md
|   |   |   |-- tool.github-request-copilot-review.md
|   |   |   |-- tool.github-resolve-review-thread.md
|   |   |   |-- tool.github-run-secret-scanning.md
|   |   |   |-- tool.github-search-code.md
|   |   |   |-- tool.github-search-commits.md
|   |   |   |-- tool.github-search-issues.md
|   |   |   |-- tool.github-search-pull-requests.md
|   |   |   |-- tool.github-search-repositories.md
|   |   |   |-- tool.github-search-users.md
|   |   |   |-- tool.github-sub-issue-write.md
|   |   |   |-- tool.github-unresolve-review-thread.md
|   |   |   |-- tool.github-update-issue-comment.md
|   |   |   |-- tool.github-update-pull-request-branch.md
|   |   |   |-- tool.github-update-pull-request.md
|   |   |   |-- tool.glob.md
|   |   |   |-- tool.gmail-apply-sensitive-message-label.md
|   |   |   |-- tool.gmail-apply-sensitive-thread-label.md
|   |   |   |-- tool.gmail-batch-get-messages.md
|   |   |   |-- tool.gmail-batch-get-threads.md
|   |   |   |-- tool.gmail-create-draft.md
|   |   |   |-- tool.gmail-create-label.md
|   |   |   |-- tool.gmail-delete-draft.md
|   |   |   |-- tool.gmail-delete-label.md
|   |   |   |-- tool.gmail-forward.md
|   |   |   |-- tool.gmail-get-draft.md
|   |   |   |-- tool.gmail-get-message.md
|   |   |   |-- tool.gmail-get-thread.md
|   |   |   |-- tool.gmail-label-message.md
|   |   |   |-- tool.gmail-label-thread.md
|   |   |   |-- tool.gmail-list-drafts.md
|   |   |   |-- tool.gmail-list-labels.md
|   |   |   |-- tool.gmail-mark-message-spam.md
|   |   |   |-- tool.gmail-mark-thread-spam.md
|   |   |   |-- tool.gmail-reply.md
|   |   |   |-- tool.gmail-search-threads.md
|   |   |   |-- tool.gmail-send-message.md
|   |   |   |-- tool.gmail-trash-message.md
|   |   |   |-- tool.gmail-trash-thread.md
|   |   |   |-- tool.gmail-unlabel-message.md
|   |   |   |-- tool.gmail-unlabel-thread.md
|   |   |   |-- tool.gmail-unmark-message-spam.md
|   |   |   |-- tool.gmail-unmark-thread-spam.md
|   |   |   |-- tool.gmail-untrash-message.md
|   |   |   |-- tool.gmail-untrash-thread.md
|   |   |   |-- tool.gmail-update-draft.md
|   |   |   |-- tool.gmail-update-label.md
|   |   |   |-- tool.gmail-update-message-labels.md
|   |   |   |-- tool.grep.md
|   |   |   |-- tool.list-agents.md
|   |   |   |-- tool.list-connectors.md
|   |   |   |-- tool.list-mcp-resources.md
|   |   |   |-- tool.list-plugins.md
|   |   |   |-- tool.list-skills.md
|   |   |   |-- tool.lsp.md
|   |   |   |-- tool.monitor.md
|   |   |   |-- tool.notebook-edit.md
|   |   |   |-- tool.notion-calendar-cancel-events.md
|   |   |   |-- tool.notion-calendar-create-events.md
|   |   |   |-- tool.notion-calendar-list-calendar-resources.md
|   |   |   |-- tool.notion-calendar-list-calendars.md
|   |   |   |-- tool.notion-calendar-list-contacts.md
|   |   |   |-- tool.notion-calendar-list-coworkers-events.md
|   |   |   |-- tool.notion-calendar-list-events.md
|   |   |   |-- tool.notion-calendar-update-events.md
|   |   |   |-- tool.notion-delete-comment.md
|   |   |   |-- tool.notion-delete-databases.md
|   |   |   |-- tool.notion-delete-pages.md
|   |   |   |-- tool.notion-get-groups.md
|   |   |   |-- tool.notion-restore-pages.md
|   |   |   |-- tool.notion-set-comment-reaction.md
|   |   |   |-- tool.notion-set-discussion-resolved.md
|   |   |   |-- tool.notion-update-comment.md
|   |   |   |-- tool.notion-update-enabled-skills.md
|   |   |   |-- tool.pdf-display.md
|   |   |   |-- tool.pdf-interact.md
|   |   |   |-- tool.pdf-list.md
|   |   |   |-- tool.powershell.md
|   |   |   |-- tool.push-notification.md
|   |   |   |-- tool.read-mcp-resource-dir.md
|   |   |   |-- tool.read-mcp-resource.md
|   |   |   |-- tool.read-notifications.md
|   |   |   |-- tool.read.md
|   |   |   |-- tool.remote-add-repo.md
|   |   |   |-- tool.remote-archive-session.md
|   |   |   |-- tool.remote-confirm-repository-trust.md
|   |   |   |-- tool.remote-create-session.md
|   |   |   |-- tool.remote-create-trigger.md
|   |   |   |-- tool.remote-delete-trigger.md
|   |   |   |-- tool.remote-fire-trigger.md
|   |   |   |-- tool.remote-get-event.md
|   |   |   |-- tool.remote-get-session.md
|   |   |   |-- tool.remote-get-trigger.md
|   |   |   |-- tool.remote-interrupt-session.md
|   |   |   |-- tool.remote-list-environments.md
|   |   |   |-- tool.remote-list-events.md
|   |   |   |-- tool.remote-list-repos.md
|   |   |   |-- tool.remote-list-sessions.md
|   |   |   |-- tool.remote-list-triggers.md
|   |   |   |-- tool.remote-read-documentation.md
|   |   |   |-- tool.remote-register-repo-root.md
|   |   |   |-- tool.remote-send-later.md
|   |   |   |-- tool.remote-send-message.md
|   |   |   |-- tool.remote-set-session-tags.md
|   |   |   |-- tool.remote-set-session-title.md
|   |   |   |-- tool.remote-subscribe-pr-activity.md
|   |   |   |-- tool.remote-trigger.md
|   |   |   |-- tool.remote-unarchive-session.md
|   |   |   |-- tool.remote-unsubscribe-pr-activity.md
|   |   |   |-- tool.remote-unwatch-url.md
|   |   |   |-- tool.remote-update-trigger.md
|   |   |   |-- tool.remote-watch-url.md
|   |   |   |-- tool.report-findings.md
|   |   |   |-- tool.schedule-wakeup.md
|   |   |   |-- tool.search-mcp-registry.md
|   |   |   |-- tool.search-plugins.md
|   |   |   |-- tool.search-skills.md
|   |   |   |-- tool.send-feedback.md
|   |   |   |-- tool.send-message.md
|   |   |   |-- tool.send-user-file.md
|   |   |   |-- tool.share-onboarding-guide.md
|   |   |   |-- tool.show-onboarding-role-picker.md
|   |   |   |-- tool.skill.md
|   |   |   |-- tool.subagent-handback.md
|   |   |   |-- tool.suggest-connectors.md
|   |   |   |-- tool.suggest-plugin-install.md
|   |   |   |-- tool.suggest-skills.md
|   |   |   |-- tool.task-create.md
|   |   |   |-- tool.task-get.md
|   |   |   |-- tool.task-list.md
|   |   |   |-- tool.task-output.md
|   |   |   |-- tool.task-stop.md
|   |   |   |-- tool.task-update.md
|   |   |   |-- tool.todo-write.md
|   |   |   |-- tool.tool-search.md
|   |   |   |-- tool.wait-for-mcp-servers.md
|   |   |   |-- tool.web-fetch.md
|   |   |   |-- tool.web-search.md
|   |   |   |-- tool.workflow.md
|   |   |   `-- tool.write.md
|   |   `-- INDEX.md
|   |-- evidence/
|   |   `-- hw1-correction-2026-10-03/
|   |       |-- README.md
|   |       |-- narration.zh.txt
|   |       |-- transcription.jsonl
|   |       `-- validate.py
|   |-- predictions/
|   |   |-- first-draft-ca80695/
|   |   |   |-- declared.json
|   |   |   |-- measured-example-bank.json
|   |   |   |-- measured.json
|   |   |   |-- new-keys.json
|   |   |   `-- summary.json
|   |   |-- replaced-be4e324/
|   |   |   |-- declared.json
|   |   |   |-- measured-example-bank.json
|   |   |   |-- measured.json
|   |   |   |-- new-keys.json
|   |   |   `-- summary.json
|   |   |-- draft-publish-first-run.md
|   |   |-- draft-publish-first-run.measured.json
|   |   |-- draft-publish-first-run.outcome.md
|   |   |-- draft-publish-first-run.prediction.json
|   |   |-- hw2-sample-pass.inputs.json
|   |   |-- hw2-sample-pass.md
|   |   |-- hw2-sample-pass.measured-example-bank.json
|   |   |-- hw2-sample-pass.measured.json
|   |   `-- hw2-sample-pass.prediction.json
|   |-- CLAUDE-CODE-PKM-HARNESS.md
|   |-- CLAUDE-CODE-PKM-TOOLS.md
|   |-- CLAUDE-CODE-PKM.md
|   |-- EXPLORE-SPEC.md
|   |-- LATEST-CONCLUSIONS.md
|   |-- OPEN-PROBLEMS.md
|   |-- OPERATION-CHAINS.md
|   |-- OPERATION-MODEL.md
|   |-- SANDBOX-FACTS.md
|   |-- TREE.md
|   `-- ZENODO-RUNBOOK.md
|-- figbank/
|   |-- app/
|   |   |-- frontier-tree/
|   |   |   |-- src/
|   |   |   |   |-- App.tsx
|   |   |   |   |-- Figure.tsx
|   |   |   |   |-- data.ts
|   |   |   |   |-- index.css
|   |   |   |   `-- main.tsx
|   |   |   |-- .gitignore
|   |   |   |-- .parcelrc
|   |   |   |-- .postcssrc
|   |   |   |-- README.md
|   |   |   |-- check_page.py
|   |   |   |-- index.html
|   |   |   |-- package.json
|   |   |   |-- pnpm-lock.yaml
|   |   |   |-- tailwind.config.js
|   |   |   |-- tsconfig.app.json
|   |   |   |-- tsconfig.json
|   |   |   |-- tsconfig.node.json
|   |   |   `-- vite.config.ts
|   |   |-- variable-model/
|   |   |   |-- src/
|   |   |   |   |-- App.tsx
|   |   |   |   |-- Figure.tsx
|   |   |   |   |-- data.ts
|   |   |   |   |-- index.css
|   |   |   |   `-- main.tsx
|   |   |   |-- .gitignore
|   |   |   |-- .parcelrc
|   |   |   |-- .postcssrc
|   |   |   |-- README.md
|   |   |   |-- check_page.py
|   |   |   |-- index.html
|   |   |   |-- package.json
|   |   |   |-- pnpm-lock.yaml
|   |   |   |-- tailwind.config.js
|   |   |   |-- tsconfig.app.json
|   |   |   |-- tsconfig.json
|   |   |   |-- tsconfig.node.json
|   |   |   `-- vite.config.ts
|   |   `-- bundle.sh
|   |-- examples/
|   |   |-- figbank-file-tree.json
|   |   |-- figbank-file-tree.pdf
|   |   |-- figbank-file-tree.png
|   |   |-- figbank-file-tree.svg
|   |   |-- gen_file_tree.py
|   |   |-- gen_majority_vote.py
|   |   |-- majority-vote-curve.json
|   |   |-- majority-vote-curve.pdf
|   |   |-- majority-vote-curve.png
|   |   |-- majority-vote-curve.svg
|   |   |-- pipeline-sequence.json
|   |   |-- pipeline-sequence.pdf
|   |   |-- pipeline-sequence.png
|   |   |-- pipeline-sequence.svg
|   |   |-- pipeline-workflow.json
|   |   |-- pipeline-workflow.png
|   |   |-- pipeline-workflow.svg
|   |   |-- round-lifecycle.json
|   |   |-- round-lifecycle.pdf
|   |   |-- round-lifecycle.png
|   |   |-- round-lifecycle.svg
|   |   `-- verdicts.jsonl
|   |-- lib/
|   |   |-- components.js
|   |   |-- figure.d.ts
|   |   |-- figure.js
|   |   |-- lifecyclelayout.js
|   |   |-- palette.d.ts
|   |   |-- palette.js
|   |   |-- plot.js
|   |   |-- plotlayout.js
|   |   |-- sequencelayout.js
|   |   |-- text.js
|   |   |-- treelayout.js
|   |   |-- vnode.d.ts
|   |   `-- vnode.js
|   |-- reader/
|   |   `-- cold-reader.md
|   |-- schema/
|   |   `-- figure.schema.json
|   |-- tests/
|   |   |-- calibration.json
|   |   |-- figure.test.js
|   |   |-- fixture-two-regions.json
|   |   |-- plot.test.js
|   |   `-- text.test.js
|   |-- README.md
|   |-- package.json
|   `-- render_svg.js
|-- harness/
|   `-- harness.html
|-- out/
|   `-- .gitkeep
|-- theory/
|   |-- LIVENESS.md
|   |-- RECORD-THEORY.md
|   |-- RESULTS.md
|   |-- liveness.py
|   `-- proto.py
|-- vendor/
|   |-- babel.js
|   |-- react.js
|   |-- reactdom.js
|   `-- tailwind.js
|-- .gitignore
|-- CITATION.cff
|-- CLAUDE.md
|-- CONTRIBUTING.md
|-- LICENSE
|-- Makefile
|-- NOTICE
|-- README.md
`-- THIRD_PARTY_NOTICES.md

33 directories, 1315 files tracked
```
