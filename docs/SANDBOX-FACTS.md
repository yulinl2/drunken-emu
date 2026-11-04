# Measured facts about the claude.ai container

*v0.1.0 · 2026-08 measurements · append-only; re-verify before trusting across months*

Everything here was run, not recalled. Each row cost a tool call; storing them
means the next session does not re-spend it. Usefulness is not the filter —
*having been verified* is.

Dates matter: this is a moving platform. Measurements are from 2026-08.

## Runtime shape

| Fact | Evidence |
|---|---|
| Ubuntu 24.04.4, kernel `6.18.44-fc-v21`, **1 vCPU**, 3.9 GiB RAM, running as `root` | `/etc/os-release`, `uname`, `nproc`, `free` |
| PID 1 is `process_api` — **not** systemd/init. Nothing runs unless a tool call runs it. | `ps -eo pid,ppid,comm` |
| The VM is **forked from a snapshot per activity burst**, not long-running | `dmesg`: `random: crng reseeded due to virtual machine fork`; `/proc/uptime` read 23 s while a file written 700 s earlier was still on disk |
| Idle timeout is roughly **3 minutes** after the last tool call, then the VM is reclaimed | a 5 s-tick probe ran 195 s past the last call, then stopped dead |

## What survives, what does not

| Across | Filesystem | Env vars | Processes |
|---|---|---|---|
| two tool calls in one turn | ✅ | ❌ fresh shell each time | `nohup` ❌ / `setsid` ✅ |
| a turn boundary | ✅ | ❌ | ✅ briefly, then killed with the VM |
| the idle timeout | ✅ (volume reattaches) | ❌ | ❌ **always** |

Consequences worth stating plainly, because they close off obvious ideas:

- **No daemon is possible.** Not with `setsid`, not with cron (`cron` is not
  installed and not running), not with anything. Background polling has to live
  somewhere with real uptime — GitHub Actions, not here.
- `~/.bashrc` is **not sourced**; a hook written there never fires. Verified
  with a marker file that stayed at 0 lines.
- There is **no hook system at all** — no `settings.json`, no pre-response
  event, no container-init event. The container is passive: it executes when a
  tool call executes and at no other time.

## Preinstalled toolchain

| Thing | Where / detail |
|---|---|
| Chromium for Playwright | **`/opt/pw-browsers/chromium-1194/chrome-linux/chrome`** — *not* `~/.cache/ms-playwright`, which is why `playwright install` looks necessary and is not |
| TeX Live 2023/Debian, 377 MB | 10 `texlive-*` deb packages, baked into the image 2024-02-14 |
| LaTeX speed | 19-page beamer deck, two passes, **3.26 s**, zero errors |
| Present | `pandoc`, ImageMagick `convert`, `node`, `python3`, `pdflatex`/`xelatex`/`latexmk` |
| Absent | `gs` (Ghostscript), `R`, `julia`, `gh` CLI, `cron`, `/usr/bin/time` |
| Missing TeX packages | `biblatex` (but `natbib` is present, which most stats journals use), `ctex` (no CJK). `apt-get` works, so both are installable per session. |

## Network

| Fact | Evidence |
|---|---|
| Egress works through a proxy; `apt` and `pip` both function | `apt-get install --dry-run` resolved, `pip download` succeeded |
| **Port 22 is blocked** — SSH and git-over-SSH are unavailable. HTTPS + token only. | `/dev/tcp/github.com/22` failed |
| `api.github.com` returns **403 without a `User-Agent` header**, 200 with one | direct comparison |
| Anonymous GitHub API rate limit 60/hr; authenticated 5000/hr | `/rate_limit` before and after adding a token |
| `git.overleaf.com` is reachable; its git smart-HTTP endpoint answers 401 unauthenticated | `info/refs?service=git-upload-pack` |

## GitHub behaviours that cost debugging time

| Behaviour | Consequence |
|---|---|
| `GET /repos/{owner}/{repo}` is cached **60 s** (`cache-control: private, max-age=60`) | A read right after a push can return the pre-push snapshot. This produced a false "GitHub did not update the default branch" conclusion and a wasted instruction to the user. **Re-sample before concluding anything about GitHub state.** |
| First branch pushed to an empty repo *does* become the default branch | Confirmed once the cache expired. No manual settings change is needed. |
| A `workflow_dispatch`-only workflow in a repo that has never run Actions may never get indexed | Chicken-and-egg: not indexed → cannot dispatch → no run → never activates. Any auto-firing trigger (`push:` or a real `schedule:`) breaks it. Confidence: **B** — the phenomenon is solid, but it was not isolated against a fresh repo. |
| Overleaf's git integration uses **`main`**, not `master` | Contradicts widely-copied advice. Do not hard-code either: resolve it with `git ls-remote --symref <url> HEAD`. |
| `workflow_dispatch` end-to-end latency | trivial job **12.4 / 12.4 / 14.8 s**; a real job doing an Overleaf fetch + merge + double push **18 s**; push→Overleaf **12 s**. An earlier estimate of ~40 s was 2–3x too pessimistic. |

## Method note

Four separate conclusions in this project were reached from a **single**
observation of a remote system and were later wrong: the default-branch reading,
the workflow-indexing cause, the vendor version strings scraped from minified
bundles, and the mount-cost constant. Every one was corrected by sampling again
or by measuring in a second environment.

Single-point observations of caching, asynchronous, or lazily-indexed systems
are not facts. Sample twice, or in two environments, before writing it down.

## 2026-08-31 (pass 4, claude.ai chats)
- GitHub `workflow_runs` JSON can contain raw control characters in string
  fields; Python `json.loads` default-strict rejects the payload. Parse with
  `strict=False`. Symptom: a poller that never sees its own run complete.
- `/mnt/project` is not a mounted path in this container even when the system
  prompt lists project files under it; `ls /mnt` shows no such directory and
  direct reads fail. Project knowledge is reachable only through the
  project-knowledge search tool. Re-confirms: disk mount state != project state.

## Added 2026-09-26

| Fact | Evidence |
|---|---|
| `page.set_content` with an inline `<svg>` inside a fixed-width `<div>` is enough to measure rendered type size — no file server, no `file://`, no screenshot. `getBoundingClientRect()` of the `<svg>` divided by `viewBox.baseVal.width` converts authored px to rendered px. | `checks/svg_legibility.py` |
| `open(f,'w').write(open(f).read().replace(...))` **truncates before the read runs** and writes an empty file; it once made a positive control fail for "no `<svg>` element" instead of the induced fault. Read into a variable first. | observed while inducing a fault |
| A positive control can fail to fire without the check being wrong: moving a label 2 authored units is 1.1 rendered px at scale 0.5588, under a 0.12 overlap tolerance. Induce the fault at a magnitude the check is specified to catch. | controls on the same figure |

## 2026-09-12 and 2026-09-26 (second environment, claude.ai project chat; appended by the WeChat-origin-corpus session)
- **`/mnt/project` DOES exist and is readable in a claude.ai chat that belongs to a project.** The 2026-08-31
  pass-4 note says it is not a mounted path; in this container `ls /mnt/project` listed 23 files on 2026-09-12
  and again on 2026-09-26, and direct reads succeed. Both observations are presumably right for their own
  container, which makes this a **per-container (project vs. non-project chat), not a platform, property**.
  Do not branch on its absence; test for it.
- Kernel moves between sessions within one series: `6.18.44-fc-v21` (pass 4), `-v32` (2026-09-12),
  `-v42` (2026-09-26). Ubuntu 24.04.4 LTS, 1 vCPU, ~3.9 GiB, root, PID 1 `process_api` unchanged.
- `/opt/pw-browsers/` also ships `chromium_headless_shell-1194` and `ffmpeg-1011` alongside `chromium-1194`.
- `time` is **not** a shell builtin under `/bin/sh` here (`sh: 1: time: not found`); wrap the command in
  `date +%s.%N` instead.
- `cron`, `gh`, `gs` absent; `pandoc`, `pdflatex`, `node` present (unchanged from pass 4).
- GitHub's anonymous **API** hits the 60/hour limit quickly, but `git clone --depth 1` over HTTPS is
  unaffected; when the API is throttled, clone instead of scraping. (2026-09-12)

Scope: two dates, one container type. By this file's own rule these are two points, not a settled fact, until a
third environment of the *non-project* kind is sampled on the same day.

## Editing pitfalls seen 2026-10-02 (TapGrade sessions)

- `open(p, "w").write(open(p).read())` truncates the file **before** it is read: the result is an empty file. Read into a
  variable first, then open for writing.
- `re.sub(pattern, repl, s)` interprets backslash escapes in `repl`: `"\n"` becomes a real newline. Patching JavaScript
  that way split `lines.join("\n")` across two lines (a syntax error). Pass a function (`lambda m: repl`) or escape it.
- Tool output is JSON-escaped: a file containing two backslashes shows four in the transcript. Count escapes in the file
  (`repr(open(p).read())`), not on screen.
- Async Playwright: `p.chromium.launch()` returns a coroutine that fails only when awaited, so a try/except around the call
  catches nothing; `checks/browser.alaunch` awaits inside the try.

## Added 2026-10-17 (Claude Code cloud session, not a claude.ai chat container)

| Fact | Evidence |
|---|---|
| A different container class from the ones above. The repository's `.claude/settings.json` registers a SessionStart hook and the harness documents command hooks (PostToolUse, Stop and others), so the "no hook system at all" row above is true of claude.ai chat containers and not of this one. | `.claude/settings.json`; <https://code.claude.com/docs/en/hooks> |
| Hooks registered mid-session in a new `.claude/settings.local.json` did **not** run: after two changes to a watched file the `emu_loop` ledger held its `arm` record and no evaluation. Whether a session that *starts* with the hooks fires them is not measured (P-dae1, question 3). One session, one container: a point, not a fact. | `out/loop/ledger.jsonl`, read after the changes |
| `python3 -c "import playwright"` fails by default here; README's "preinstalled" is true of claude.ai chat containers. `pip install playwright` gave 1.64.0, and `bin/emu smoke` then exited 1 at `p.chromium.launch` (`checks/smoke.py:23`; `checks/browser.alaunch` is not used there). `pip install playwright==1.56.0`, the build that matches the shipped `chromium-1194` and `ffmpeg-1011`, made the same command exit 0 in 2.67 s. | the same command before and after, in one container |
| `pip install` works here (playwright, pytest and the 1.56.0 pin). | the installs above |
| A disarmed `emu_loop` hook costs 55.2 ms per tool call, mean of 20 runs, Python start-up included. | `python3 checks/emu_loop.py hook post-edit < /dev/null`, 20 times |
| A hook outside this kit, `~/.claude/stop-hook-git-check.sh`, ran at the end of a turn and its stderr with exit code 2 reached the model as "Stop hook feedback". It reads `stop_hook_active` from the stdin JSON (exit 0 when true) and flags, in this order: uncommitted changes, untracked files (`git ls-files --others --exclude-standard`), commits GitHub would show as Unverified when signing is configured, unpushed commits. No settings file under `/etc/claude-code`, `/root/.claude` or `/home/user/.claude` registers it (none exists there). | the message received; the script, lines 7-10, 26-37, 77-124 |
| `$CLAUDE_PROJECT_DIR` is unset in the Bash tool's environment (documented for command hooks, not for the Bash tool). | `echo "${CLAUDE_PROJECT_DIR-<unset>}"` |

## Added 2026-10-18 (Claude Code cloud session, the same container class)

| Fact | Evidence |
|---|---|
| `git push origin --delete <branch>` through the session's git proxy prints "Everything up-to-date", exits 0 and **deletes nothing**: `git fetch --prune` still lists the branch. On 2026-09-28 the same attempt ended "remote end hung up" (#24). The session's GitHub tools have no branch delete either. Deleting a branch is the owner's job, on GitHub. | `attempt/plot-native` and `theory/record-model` (both merged), 2026-10-18 |
| The 2026-10-17 row's smoke failure (`p.chromium.launch` with pip's Playwright 1.64 against Chromium 1194) is fixed on main. Every launch now goes through `checks/browser.py`, and `checks/test_launch_sites.py` fails on one that does not. | #78 |
| The full Chromium 1194, launched headless by `executable_path`, fetches `/favicon.ico`; the headless shell of the same build (141.0.7390.37) does not. The harness server answers 404, and `smoke.py` counted that console error against every page. `browser.py` now tries `chromium_headless_shell-*` first for a headless launch, as Playwright's own default does. | `out/server.log`: `GET /favicon.ico → 404`; with `PW_CHROMIUM=…/headless_shell`, `js_errors` was `[]` |
| In Chromium 141, a control inside a **closed `<details>`** keeps a non-empty box (18 × 80.5 px) and computed `visibility: visible`; only `checkVisibility()` returns false. A check that tests the box counts it as visible. | #76, #79 |
| None of `/usr/bin/python3` 3.11, 3.12 or 3.13 has `pytest` or `playwright`. This works: `python3 -m venv DIR` (it rejects `-q`), then `DIR/bin/pip install pytest pyyaml playwright`, then `DIR/bin` first on `PATH`, because `bin/emu` runs whichever `python3` it finds there. | this session's setup |
| After a merge conflict in `docs/TREE.md`, run `bin/gen_tree.py --write` only once the index is clean. While the conflict stands, the index holds the file's stage 1, 2 and 3 entries, and the generated index is wrong (`--check` failed right after `--write`). Resolve the conflict, `git add`, then regenerate. | the merge of #78 into #77 |
| The GitHub merge tool's `expectedHeadSha` takes the full 40-character SHA; a 7-character one is refused before any merge is tried. | 2026-10-18 |
