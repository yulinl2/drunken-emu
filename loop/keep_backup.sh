#!/usr/bin/env bash
# keep backup: the unconditional backup of what lives only in this machine, run by loop/keep.py at every stop (loop.json: stop_runs).
# Into the project's repository, branch PREFIX + SID (SID: the first 8 characters of the newest transcript's name), through its own
# worktree in the state directory, so the working branch is never touched: the session transcripts (LOOP_TRANSCRIPTS_DIR), the
# folders of LOOP_EXTRA_DIRS (one per line; each is stored under its own name), the working branch's status, its stashes as
# patches, and its untracked files.
# It decides nothing; the one rule is mechanical: a file over 20 MB is listed (size, sha256) instead of stored, because GitHub
# refuses files over 100 MB. One run at a time, in the background. LAST-RUN (line 1) says "running since T" while a run goes (line 2:
# the outcome of the run before, so that the pushed commit carries it), then "ok T" only after the copies, the commit and the push
# all succeeded, else "FAILED T: step S". A nested repository (a folder that holds .git, a directory or a pointer file) is listed in
# NESTED.tsv and never copied. A copy whose source is gone leaves the copy only after a pushed commit holds it.
# Environment, set by loop/keep.py from loop.json: LOOP_ROOT, LOOP_REMOTE, LOOP_PREFIX, LOOP_EXTRA_DIRS, LOOP_TRANSCRIPTS_DIR,
# LOOP_STATE_DIR. A missing one stops the run: a backup that cannot name its inputs is a failure, not a pass.
# Usage: bash loop/keep_backup.sh [--wait]   (--wait holds the call until the background body ends)
set -u
: "${LOOP_ROOT:?LOOP_ROOT is not set}" "${LOOP_REMOTE:?LOOP_REMOTE is not set}" "${LOOP_TRANSCRIPTS_DIR:?LOOP_TRANSCRIPTS_DIR is not set}" "${LOOP_STATE_DIR:?LOOP_STATE_DIR is not set}"
PREFIX="${LOOP_PREFIX-}"
[ -n "$PREFIX" ] || { echo "refused: the backup prefix is empty (a backup names its branches by prefix)" >&2; exit 2; }
R="$LOOP_ROOT"; REMOTE="$LOOP_REMOTE"; TDIR="$LOOP_TRANSCRIPTS_DIR"; STATE="$LOOP_STATE_DIR"
T="${LOOP_TRANSCRIPT-}"; [ -n "$T" ] && [ -f "$T" ] || { echo "refused: no transcript is named (LOOP_TRANSCRIPT): a backup is of one session, the one that asked for it" >&2; exit 2; }
SID=$(basename "$T" .jsonl | cut -c1-8); BR="$PREFIX$SID"; W="$STATE/backup-wt-$SID"; LOCK="$STATE/backup-$SID.lock"; LOG="$STATE/backup-$SID.log"
EXTRA=(); while IFS= read -r x; do [ -n "$x" ] && EXTRA+=("$x"); done <<< "${LOOP_EXTRA_DIRS-}"
(
  exec 9>"$LOCK"; if [ "${1:-}" = --wait ]; then flock -w 100 9; else flock -n 9; fi || { echo "skipped $(date -u +%FT%TZ): the previous run is still going"; exit 0; }
  if [ ! -e "$W/.git" ]; then
    if git -C "$R" ls-remote --exit-code "$REMOTE" "refs/heads/$BR" >/dev/null 2>&1; then
      git -C "$R" fetch -q "$REMOTE" "$BR:$BR" && git -C "$R" worktree add -q "$W" "$BR"
    else
      git -C "$R" worktree add -q --detach "$W" && git -C "$W" checkout -q --orphan "$BR" && git -C "$W" read-tree --empty
      git -C "$W" sparse-checkout disable 2>/dev/null; find "$W" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
    fi
  fi
  # LAST-RUN lives in the worktree, so a run that cannot make one reports through a status file beside it; keep.last_run reads both
  [ -e "$W/.git" ] || { echo "FAILED $(date -u +%FT%TZ): no worktree for $BR, see $LOG" | tee "$STATE/backup-$SID.status"; exit 0; }
  rm -f -- "$STATE/backup-$SID.status"
  gd=$(git -C "$W" rev-parse --absolute-git-dir 2>/dev/null) && [ -e "$gd/index.lock" ] && { rm -f -- "$gd/index.lock"; echo "removed a stale $gd/index.lock (this run holds $LOCK; a run killed inside git leaves one)"; }
  prev=$(head -n 1 "$W/LAST-RUN" 2>/dev/null); printf 'running since %s\nprevious run: %s\n' "$(date -u +%FT%TZ)" "${prev:-none}" > "$W/LAST-RUN"; ok=1
  put() { local src="$1" dst="$2" n; case "$dst/" in */.git/*) return 0;; esac; n=$(stat -c %s -- "$src" 2>/dev/null) || { [ -e "$src" ] && ok=0; return 0; }; mkdir -p "$(dirname "$dst")"   # never a file named .git, nor one inside a .git
          if [ "$n" -gt 20971520 ]; then printf '%s\t%s\t%s\n' "$n" "$(sha256sum "$src" | cut -c1-64)" "$src" >> "$W/LARGE.tsv"; else cp -a "$src" "$dst" || { [ -e "$src" ] && ok=0; }; fi; }   # a source gone since find listed it is no failure
  : > "$W/LARGE.tsv"; : > "$W/NESTED.tsv"; touch "$W/LEFT-OUT.txt"; declare -A SRC; tab=$'\t'
  # transcripts are stored whole, in 16 MB parts: as single files they would only be listed past 20 MB;
  # earlier parts stay byte-identical while a transcript grows, so git stores them once. A transcript that comes back shorter (a
  # compaction rewrote one shorter) does not overwrite the longer copy: that is renamed .until-<time> and kept.
  T0=$(date -u +%Y%m%dT%H%M%SZ)
  # also the transcripts of the agents a session starts (*/<session>/subagents/*.jsonl)
  # which transcripts: the session's own, with those of the agents and workflows it started. Every transcript under the
  # transcripts folder only where the project says that every session on this machine is its own (LOOP_SESSIONS=all).
  if [ "${LOOP_SESSIONS-here}" = all ]; then FILES=("$TDIR"/*/*.jsonl "$TDIR"/*/*/subagents/*.jsonl "$TDIR"/*/*/subagents/workflows/*/*.jsonl)
  else FILES=("$T" "${T%.jsonl}"/subagents/*.jsonl "${T%.jsonl}"/subagents/workflows/*/*.jsonl); fi
  for f in "${FILES[@]}"; do [ -f "$f" ] || continue; n="$(basename "$(dirname "$f")")__$(basename "$f")"; d="$W/transcripts/$n.parts"; s=$(stat -c %s "$f")
    if [ -f "$W/transcripts/$n" ]; then   # the single-file copy of an earlier run
      if [ "$(stat -c %s "$W/transcripts/$n")" -gt "$s" ]; then mv "$W/transcripts/$n" "$W/transcripts/${n%.jsonl}.until-$T0.jsonl"; else rm -f "$W/transcripts/$n"; fi; fi
    [ "$(cat "$d"/part-* 2>/dev/null | wc -c)" -gt "$s" ] && mv "$d" "$W/transcripts/${n%.jsonl}.until-$T0.parts"
    mkdir -p "$d"; rm -f "$d"/part-*; split -b 16m -d -a 3 "$f" "$d/part-" || ok=0; done
  for s in "${EXTRA[@]}"; do
    [ -d "$s" ] || continue; k="$(basename "$s")"
    if [ -z "$k" ] || [ "$k" = . ] || [ -n "${SRC[$k]:-}" ]; then echo "refused the extra folder $s: its name is empty or already taken" >> "$LOG"; ok=0; continue; fi
    SRC[$k]="$s"
    mapfile -d '' nest < <(cd "$s" && find . -mindepth 1 -name .git -prune -printf '%h\0')   # every folder that holds .git (a directory or a pointer file)
    for r in "${nest[@]}"; do g="$s/${r#./}/.git"; if [ -d "$g" ]; then v="dir $(head -n 1 "$g/HEAD" 2>/dev/null)"; else v="file $(head -n 1 "$g" 2>/dev/null)"; fi
      printf '%s\t%s\t%s\n' "$k" "${r#./}" "$v" >> "$W/NESTED.tsv"; done
    while IFS= read -r -d '' f; do
      for r in "${nest[@]}"; do [ "$r" = . ] || case "$f" in "$r"/*) continue 2;; esac; done   # inside a nested repository: not copied
      put "$s/${f#./}" "$W/extra/$k/${f#./}"
    done < <(cd "$s" && find . -name .git -prune -o -type f -print0)
  done
  mkdir -p "$W/git"; { date -u +%FT%TZ; git -C "$R" rev-parse --abbrev-ref HEAD; git -C "$R" log -1 --format='%h %s'; git -C "$R" status --porcelain; git -C "$R" stash list; } > "$W/git/state.txt"
  git -C "$R" diff HEAD > "$W/git/working.patch" 2>/dev/null   # changes to tracked files not yet committed
  i=0; while git -C "$R" rev-parse -q --verify "stash@{$i}" >/dev/null 2>&1; do git -C "$R" stash show -p --include-untracked "stash@{$i}" > "$W/git/stash-$i.patch" 2>/dev/null; i=$((i+1)); done
  while IFS= read -r -d '' f; do   # git lists an untracked nested repository as one entry ending in /: listed, not copied
    case "$f" in */) printf '%s\t%s\t%s\n' git/untracked "$f" "nested repository in $R" >> "$W/NESTED.tsv"; continue;; esac; put "$R/$f" "$W/git/untracked/$f"
  done < <(cd "$R" && git ls-files --others --exclude-standard -z)
  # the git steps. A nested repository still in the worktree is never added: its link leaves the index (update-index --force-remove)
  # and its folder is listed in LEFT-OUT.txt and left out of every later add
  step=""; [ "$ok" = 1 ] || step="copy"
  mapfile -d '' gl < <(git -C "$W" ls-files -s -z | while IFS= read -r -d '' e; do [ "${e%% *}" = 160000 ] && printf '%s\0' "${e#*"$tab"}"; done)
  mapfile -d '' nw < <(cd "$W" && find extra git -mindepth 1 -name .git -prune -printf '%h\0' 2>/dev/null)
  for p in "${gl[@]}" "${nw[@]}"; do grep -qxF -- "$p" "$W/LEFT-OUT.txt" || { echo "$p" >> "$W/LEFT-OUT.txt"; echo "left out of the backup from now on (nested repository in the worktree): $p"; }; done
  [ ${#gl[@]} -eq 0 ] || git -C "$W" update-index --force-remove -- "${gl[@]}" || step="${step:+$step, }git update-index"
  ex=(); while IFS= read -r p; do [ -n "$p" ] && ex+=(":(exclude,literal)$p"); done < "$W/LEFT-OUT.txt"
  git -C "$W" add -A -- . "${ex[@]}" || step="${step:+$step, }git add"
  who=""; git -C "$W" config user.email >/dev/null 2>&1 || who="-c user.name=loop-keep-backup -c user.email=loop-keep-backup@localhost.invalid"   # a machine with no git identity must still be able to commit its backup; a configured one is used as it is
  git -C "$W" diff --cached --quiet || git -C "$W" $who -c gc.auto=0 -c maintenance.auto=false commit -q -m "backup $(date -u +%FT%TZ)" || step="${step:+$step, }git commit"
  case "$BR" in "$PREFIX"?*) git -C "$W" push -q "$REMOTE" "$BR" || step="${step:+$step, }git push" ;; *) step="${step:+$step, }git push (branch outside the prefix)" ;; esac
  if [ -z "$step" ]; then   # prune: a copy whose source is gone, only now that the pushed commit holds it; transcripts/ and git/ are never pruned
    np=0; while IFS= read -r -d '' p; do k="${p#extra/}"; k="${k%%/*}"; s="${SRC[$k]:-}"; [ -n "$s" ] || continue
      [ -f "$s/${p#extra/"$k"/}" ] || { rm -f -- "$W/$p" && np=$((np+1)); }; done < <(git -C "$W" ls-files -z -- extra/)
    [ "$np" = 0 ] || echo "pruned $np copies whose source is gone (each is in the pushed commit; the next commit records the removal)"
    echo "ok $(date -u +%FT%TZ)" > "$W/LAST-RUN"
  else echo "FAILED $(date -u +%FT%TZ): step $step, see $LOG" > "$W/LAST-RUN"; echo "FAILED $(date -u +%FT%TZ): step $step"; fi
) >> "$LOG" 2>&1 &
[ "${1:-}" = --wait ] && wait   # --wait: hold the call until the body ends
exit 0
