# checks/emu_loop.py: where each of its tests went

Retired 2026-11-10. `checks/emu_loop.py` is now a stub of under 30 lines: every invocation exits 0 and prints `emu_loop is retired: run python3 -I bin/loop hook install (loop/README.md)`. The loop is `loop/` (`loop/watch.py`, `loop/hook.py`). The old module had **29** tests in `checks/test_emu_loop.py` at 5a277e0 (`grep -c "^def test_"`; the ledger's "24" dates from 2026-10-18). The rows cover all 29, in file order.

Each row names the test that pins the same behaviour for `loop watch` (`loop/tests/test_watch.py` or `test_hook.py`), or `added:` for a test this change adds, or `dropped:` with why the behaviour has no counterpart. Rules the engine itself keeps are pinned in `checks/test_verdict.py`, which `loop watch` runs as a check.

| # | The old test | The behaviour it pins | Pinned now by |
|---|---|---|---|
| 1 | `test_dominates` | a candidate dominates another only if it is no worse on each shared axis and better on one | `loop/tests/test_watch.py::test_dominates` |
| 2 | `test_chain_layer_separates_the_known_bad_chain_from_the_known_good_one` | the chain layer ranks the known-bad fixture above the known-good one, on findings and load | added: `test_watch.py::test_the_engine_verdict_fails_the_known_bad_chain_and_passes_the_known_good_one_through_watch` |
| 3 | `test_smoke_layer_tells_a_broken_harness_from_a_broken_page` | a broken harness (no verdict) is not evaluated; a broken page fails; a clean run passes | `loop/tests/test_watch.py::test_a_check_that_cannot_run_is_not_a_pass` |
| 4 | `test_disarmed_hooks_are_inert` | with nothing watched, the hooks do nothing and write no ledger | `loop/tests/test_watch.py::test_inert_with_an_empty_list` |
| 5 | `test_post_edit_feeds_back_goes_quiet_and_then_sees_an_improvement` | a post feeds the verdict back once, stays quiet on unchanged bytes and reports an improvement | `loop/tests/test_watch.py::test_post_feeds_back_goes_quiet_on_unchanged_bytes_and_sees_an_improvement` |
| 6 | `test_stop_is_refused_until_the_round_cap_then_released` | a stop is refused up to the cap, then released | `loop/tests/test_watch.py::test_a_stop_is_refused_until_the_cap_then_released` |
| 7 | `test_stop_allows_a_passing_candidate` | a stop lets a passing candidate through | `loop/tests/test_watch.py::test_a_stop_allows_a_passing_candidate` |
| 8 | `test_a_dominated_candidate_is_a_regression_and_blocks_the_stop` | a dominated candidate is a regression and blocks the stop | `loop/tests/test_watch.py::test_a_dominated_candidate_blocks_the_stop` |
| 9 | `test_a_missing_trial_is_not_a_pass` | a missing trial chain is not a pass: NOT EVALUATED, and the stop is refused | added: `test_watch.py::test_a_missing_trial_chain_holds_the_stop_through_watch` |
| 10 | `test_ledger_is_append_only_and_each_record_supersedes_the_last` | the ledger is append-only; each record supersedes the last and keeps its judged bytes | `loop/tests/test_watch.py::test_the_ledger_is_append_only_and_each_record_supersedes_the_last` |
| 11 | `test_the_cli_hook_prints_one_json_object` | a post prints one JSON object whose hookSpecificOutput carries the feedback | added: `test_watch.py::test_the_post_output_names_the_event_it_answers_and_exits_0` |
| 12 | `test_a_broken_hook_fails_open_and_says_so` | a broken hook fails open and says so | `loop/tests/test_watch.py::test_a_judge_that_breaks_fails_open_and_says_so` |
| 13 | `test_arm_and_disarm_leave_a_trail` | arm and disarm leave a trail; an arming with nothing to run is refused | dropped: there is no arm or disarm, since the watched files are the entries of `loop.json`, which is under git; the refusal of an empty run is `test_watch.py::test_a_malformed_watch_entry_is_refused` |
| 14 | `test_install_is_idempotent_and_keeps_other_hooks` | install keeps other hooks and is idempotent | `loop/tests/test_hook.py::test_other_hooks_stay_and_an_earlier_copy_of_ours_is_replaced_not_doubled` |
| 15 | `test_the_why_names_what_broke_not_the_banner_around_it` | the feedback names the error line of a check that did not run, not only the banner after it | added: `test_watch.py::test_a_check_error_under_a_banner_still_reaches_the_session` |
| 16 | `test_install_keeps_the_local_file_out_of_what_the_harness_stop_hook_flags` | install keeps its local settings file out of git status | dropped: the local file is gone; install writes the user settings (outside the repository) or `--project`'s checked-in `.claude/settings.json` |
| 17 | `test_a_watched_artifact_that_disappears_is_not_a_pass` | a watched file that disappears is not a pass; the stop is refused | `loop/tests/test_watch.py::test_a_watched_file_that_disappears_is_not_a_pass` |
| 18 | `test_a_verdict_is_reused_only_under_the_same_layers` | a verdict is reused only under the same layers (here: the same command) | `loop/tests/test_watch.py::test_a_verdict_is_reused_only_under_the_same_command` |
| 19 | `test_install_keeps_a_command_that_shares_a_group_with_the_hook` | install keeps a user's command that shares a group with the hook | added: `test_hook.py::test_install_keeps_a_command_that_shares_a_group_with_ours_and_the_group_matcher` |
| 20 | `test_install_user_writes_absolute_commands_into_the_user_settings` | a user install writes absolute commands and no project-directory variable | `loop/tests/test_hook.py::test_registered_commands_carry_the_project_root_and_this_bin_loop` |
| 21 | `test_install_user_keeps_other_hooks_and_every_other_key` | a user install keeps every other key and the other hooks of each event | `loop/tests/test_hook.py::test_install_keeps_other_keys_and_a_second_run_changes_nothing` (other hooks: row 14) |
| 22 | `test_install_user_run_twice_leaves_one_entry_per_event` | a second user install leaves one entry per event | `loop/tests/test_hook.py::test_install_keeps_other_keys_and_a_second_run_changes_nothing` (second run byte-identical) |
| 23 | `test_install_user_and_shared_together_are_refused` | `--user` and `--shared` together are refused | added: `test_hook.py::test_install_refuses_user_and_project_together` |
| 24 | `test_install_user_leaves_the_repository_and_its_exclude_file_alone` | a user install leaves the repository and its exclude file alone | added: `test_hook.py::test_a_user_install_writes_nothing_under_the_project_root` |
| 25 | `test_a_new_arming_gets_its_own_rounds_even_within_the_same_second` | a new arming gets its own rounds, even within the same second | `loop/tests/test_hook.py::test_stop_refuses_a_failing_blocker_exactly_stop_cap_times_then_lets_through_and_rearms` |
| 26 | `test_a_pass_under_other_layers_is_no_baseline_for_a_regression` | a pass under other layers is no baseline for a regression | `loop/tests/test_watch.py::test_a_pass_under_another_command_is_no_baseline` (the one-frontier listing: dropped, see notes) |
| 27 | `test_the_feedback_counts_stop_refusals_against_the_cap_not_evaluations` | the feedback counts stop refusals against the cap, not evaluations | `loop/tests/test_watch.py::test_the_feedback_counts_stop_refusals_not_evaluations` |
| 28 | `test_a_pass_that_a_later_verdict_replaced_is_no_baseline` | a pass that a later verdict replaced is no baseline | `loop/tests/test_watch.py::test_a_pass_that_a_later_verdict_replaced_is_no_baseline` (frontier listing: dropped, see notes) |
| 29 | `test_the_restore_hint_never_restores_half_a_candidate` | a restore hint never restores half a candidate (artifact and trial) | added: `test_watch.py::test_a_regression_offers_no_one_line_restore_when_its_inputs_differ` (with a change to `loop/watch.py`) |

## Notes

- **A change in behaviour, on purpose (row 29).** `loop/watch.py` `block()` now withholds the one-line restore of a regression when the dominated record's inputs differ from the inputs on disk now. Before, it offered the copy regardless, which restores the file but not the candidate.
- **Rows the engine keeps (`checks/test_verdict.py`).** Rows 2, 3, 9 and 15 are pinned there under the same names, for the verdict that watch runs.
- **Not carried over.** The arm and disarm trail (13), the local settings file and its exclude entry (16), and the listing of one frontier per config in `status` (26, 28). `status` now shows each file's newest record and whether another record dominates it.
- **Known difference.** The old "why" line chose the error line over a banner. `loop watch` shows the last 20 lines (2000 characters) of a check's output, so an error more than 20 lines above the end of the output is not named.
- **Old registrations stay.** `hook install` replaces only commands that name `bin/loop`. An entry of the old module (in the project's `.claude/settings.local.json` by default) keeps calling the stub until it is removed by hand.
- **Untracked settings.** `hook install --project` writes the checked-in `.claude/settings.json`; until it is committed, the harness's untracked-file check flags it (`docs/SANDBOX-FACTS.md`, 2026-10-17).
- **Stop notices.** The stub's stop message goes to stdout with exit 0, the channel the old round-cap notice used. Whether the harness shows exit-0 stop output to the model was not measured (P-dae1, question 3).
