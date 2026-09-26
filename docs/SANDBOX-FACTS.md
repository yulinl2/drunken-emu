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
