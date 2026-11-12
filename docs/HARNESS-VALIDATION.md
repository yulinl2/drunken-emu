# Extraction validation and limits

This is the check record for the source branch derived from
[PR #85](https://github.com/yulinl2/drunken-emu/pull/85). It separates the
upstream CI observation, local executions, and behavior still unknown. The
exported `MANIFEST.json` records the exact source commit and bytes delivered.

## Checks

| Evidence | Result | Scope |
|---|---|---|
| PR #85 at `9a483c0`, GitHub push and PR CI | succeeded, observed 2026-11-11 | Upstream runner at that historical commit. |
| PR #85 at `d444a00`, GitHub push and PR CI | [push](https://github.com/yulinl2/drunken-emu/actions/runs/43027275515) and [PR](https://github.com/yulinl2/drunken-emu/actions/runs/43027285965) succeeded, observed 2026-11-12 | Upstream runner, before the extraction commit. |
| Unmodified `9a483c0`, Python 3.12, `pytest -q loop/tests` | 485 passed | Local baseline before adapter extraction. |
| Unmodified engine, browser-free checks | 335 passed | Engine protocol and chain fixtures, not live reader outcomes. |
| Real Chromium static-page controls | 5 passed with `PW_CHROMIUM=/usr/bin/chromium` | Source-preserving HTML across CLI modes; planted small control and JavaScript error detected. The bundled Playwright browser revision was unavailable in this executor. |
| Relocated export integration checks | 4 passed again after the PR head advanced | New directory and isolated HOME; PASS, FAIL and NOT EVALUATED; checker and policy byte changes; inventory corruption and symlink refusal; no overwrite. |
| Full merged loop and export suite, `083a4bf` atop `d444a00`, Python 3.12.14 | 673 passed in 64.84 s | Local source branch before the final packaging/doc edits; one external pytest deprecation warning. |
| Relocated package commands | passed in an isolated HOME | All eight verb help commands, `doctor`, `gate selftest`, `hook install --user --dry-run`, `watch eval/status`, and manifest verification. No hook installed. |
| Final exported package manifest | PENDING | Verify after source tree is complete and committed. |

The three upstream commits from `9a483c0` through `d444a00` do not change
`checks/verdict.py`, `checks/static_target.py`, `checks/test_static_targets.py`
or `bin/emu`. That comparison supports retaining the browser check as evidence
for those files, but it does not turn it into a new run at the final commit.

## What the checks cannot establish

- A command returning PASS can still use a bad evaluator, unlisted input, or an
  interpretation of the goal the principal did not authorize. Numeric dominance
  uses shared declared axes; it does not prove a better outcome for a reader.
- A checksum detects a changed exported file against the manifest. The manifest
  is unsigned, and it does not measure how the host delivers hooks.
- Hook tests feed synthetic events. One recorded live Claude session observed
  capped Stop refusals, guard refusal and backup; it did not show PostToolUse
  feedback in 34 calls. This export has not established live behavior in Codex.
- POSIX locking and Linux bash/GNU backup dependencies were exercised here;
  macOS and other hosts remain unverified.

These limits are research questions and integration boundaries, not reasons to
discard the working mechanisms. The [history](HARNESS-HISTORY.md) links the
observations, rejected claims, test migration and open scientific tests.
