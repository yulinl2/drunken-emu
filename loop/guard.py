"""The guard verb: refuse a merge, a write to a protected branch and a rewritten history unless a verdict recorded before the act covers that exact call.
Two subcommands. `pre` is a PreToolUse hook: it reads the hook's payload (JSON) on standard input and prints a deny or an ask, or nothing; it never allows. `permissions apply` merges a rules file into a user settings file. It is a tripwire against accidents, not a barrier: a verdict is self-attested, and the principal decides what a verdict says.

INVARIANT: a guarded act (a merge through a pull request, a write to a protected branch, a push that forces, deletes or mirrors, a gh write) is denied unless a go verdict in the configured verdict file (loop.json key "verdicts") was recorded before it and names that exact head or command; a permission file is written only when its rules check, and no rule in it allows what the guard decides.
FAILS WHEN: such an act passes with no verdict that names it, or a call that mentions push, merge or api passes after an internal failure; the forms listed under "Known gaps" pass as well. The tests are loop/tests/test_guard.py.

usage: python3 -I bin/loop guard pre                  (the hook payload on standard input)
       python3 -I bin/loop guard permissions apply --rules FILE [--settings FILE] [--check]
  --settings defaults to ~/.claude/settings.json; --check says what would change and writes nothing.

Matcher: Bash, and mcp__github__ merge_pull_request, push_files, create_or_update_file, delete_file. The Artifact tool asks for a delete or a force publish.
Rules (what stops without a verdict, what passes with one):
  merge_pull_request          passes only with merge_method "merge", expectedHeadSha equal to the `head` of a `merge` verdict for the same repo and PR, and a commit_message that contains the verdict's id
  push_files, create_or_update_file, delete_file     denied when the branch is a protected one (or is not named: GitHub then uses the default branch)
  git push to a protected branch    denied, explicit or implied (merge through a PR), except a push of a literal 40-hex sha (git push origin <sha>:refs/heads/main; no +, no force flag, nothing but plain pushes in the same command) whose sha is the head of a go verdict of kind merge; git itself refuses a push that is not a fast-forward
  git push that forces or deletes (--force*, --delete, -f, -d, a refspec with + or an empty source)    passes only when a `command` verdict equals the whole Bash string and the string carries --force-with-lease=<ref>:<40 hex>
  git push --mirror, --all, --branches, --prune, a wildcard or unreadable refspec, a configured mirror or push.default=matching     denied
  gh pr merge                 denied: merge through a PR
  gh api writes (-X or --method other than GET, -f, -F, --field, --raw-field, --input), gh repo edit     pass only when a `command` verdict equals the whole Bash string
  a heredoc body or a python -c body that mentions git ... push or gh ... merge/api (within 80 characters)     denied: run it as its own command (the parser does not read what a script does)
  amend, --no-verify, -n      not checked (a pushed amend needs a force push; this clone has no git hooks)
A failure denies: an exception on a call that mentions push, merge or api, and a verdict file that cannot be read. A payload that is empty or not JSON is not checked: exit 0, with a note on standard error.
Protected branches: loop.json key "protected_branches" (default ["main", "master"]).
Verdicts: the file at loop.json key "verdicts" (default loop-state/verdicts.jsonl under the project root), one JSON object per line, append-only; a withdrawal is a new line {"verdict":"withdrawn","of":"<id>"}. A line counts when `id`, `by`, `answer` and `undo` are non-empty strings and verdict is "go":
  {"id":"v-0001","at":"...","by":"advisor example","answer":"advisor-answers/example.md","repo":"alice/project-x","kind":"merge","pr":7,"head":"<40 hex>","base":"<40 hex>","tree":"<40 hex>","tests":"12 OK","verdict":"go","undo":"git revert -m 1 <merge sha>"}
  {"id":"v-0002","at":"...","by":"reviewer <review url>","answer":"advisor-answers/example-2.md","repo":"alice/project-x","kind":"command","command":"git push --force-with-lease=topic-old:<40 hex> origin :topic-old","verdict":"go","undo":"git push origin <40 hex>:refs/heads/topic-old"}
A verdict is self-attested: this is a tripwire against accidents, not a barrier.
Why a parser: the glob rules in a permission file cannot read clustered flags (-vf, -qd), an abbreviated option (--dele), a wildcard refspec, a wrapper such as `bash -lc`, or a destination that is only implied (git push, git push origin HEAD, a branch that tracks a protected branch, a remote whose push refspec is configured). This reads the command and the repository's push configuration.
Every simple command is looked at (split at ; && || | and newlines; a # comment is dropped the way bash drops it, before a backslash-newline joins two lines: a # that begins a word outside quotes and backticks runs to the end of its line, a backslash at that end included, and a # inside a word (foo#bar, ${#v}, $#) is text; heredoc bodies and quoted text are not commands, except as the heredoc and python -c rule above says; `bash -c '...'`, `sh -ec '...'` and `bash -lc '...'` are looked into, and so are the other forms listed under Followed too; `cd DIR` and `git -C DIR` set the folder). It acts on
  - a flag that forces, deletes, mirrors, prunes or sends everything: --force*, --delete, --mirror, --prune, --all, --branches (or any abbreviation git would accept, such as --dele), or a short cluster holding f or d;
  - a refspec that starts with +, has an empty source (a delete), contains a `*`, or has a protected branch as its destination;
  - an implied destination (no refspec, or HEAD) when the current branch is protected or tracks one;
  - no refspec while the repository decides: remote.<name>.push holds a refspec that fails the tests above, remote.<name>.mirror is true, or push.default is matching;
  - a refspec that cannot be read (a $ or a backtick in it), or a command that cannot be tokenised and mentions git push.
Write the branch name out in a push command: a variable cannot be read.
Followed too: eval, backticks, xargs (its arguments come from stdin), a wrapper and its own arguments (env -i, sudo -u x, nice -n 5, timeout -k 5 60, stdbuf -oL, setsid, ionice -c3, flock FILE), shell keywords (if/then/do/{ ... }), git aliases (-c alias.x=push, alias.x in the configuration), and a program given by path (tools/git).
Scope: under loop.json "sessions": "here" the guard reads a session inside the project (its working directory at the call is the root or under it), a payload that names no working directory, and any command that names the root as an absolute path. Known gap of that scope: from a session outside the project, a push that reaches the project by a relative path (cd ../proj && git push ..., git -C ../proj push ...) and every MCP merge or file write pass with nothing said. Under "sessions": "all" every session is read.
Known gaps (not covered). The gaps the reviews found are kept with the project that uses this package; the list here is the part found so far and may be shorter: a script or make target that pushes on the caller's behalf, a gh alias, git configuration supplied by the environment (GIT_CONFIG_*) or by -c remote.<name>.push=..., a command built from variables or with its name split by quotes or a backslash (it acts only when the push itself is visible), a command line handed to a shell as data (echo '...' | bash, bash <<< '...'), a wrapper that is not in WRAPPERS or that runs a command string (su -c, script -c, flock -c, strace), a destination spelled heads/main; after a wrapper's own argument, only a shell, git or gh given by path is followed (not python, xargs or git-core/git-push by path), and git-push given by path is not read without a wrapper either; a command built with $'...', env -S, or nested past two levels (a bash -c or an eval inside two others); a $(...) or backtick after a cd in the same command line, which is read in the folder the line starts in; a push in quotes after an unquoted $(...) or backtick in the words of an eval or a bash -c (eval $(true) 'git push ...', eval `true`'git push ...'); what follows, in the body of a $(...), an unbalanced parenthesis outside quotes (a case pattern: case y in y) ...) or a double-quoted ) inside a $(...) that is itself in double quotes in that body (echo "$(echo "$(echo ")")"; ...).
A command substitution $(...) (nested ones too) and a backtick substitution are read, and a ) in quotes or after a backslash inside a body does not end it (except the double-quoted ) of the Known gaps); a $(...) or backtick inside single quotes or in a comment is read anyway (echo '$(git push -f origin x)'), and so is an escaped \\$(...) or \\`...\\` in double quotes, where bash leaves it as text, and a $( that is never closed is read to the end of the line: a false deny, in the safe direction."""
import argparse, json, os, pathlib, re, shlex, subprocess, sys, tempfile
from loop import config

LONG = ("--force", "--force-with-lease", "--force-if-includes", "--delete", "--mirror", "--prune", "--all", "--branches")
DENY_LONG = {"--mirror", "--prune", "--all", "--branches"}       # the rest of LONG forces or deletes
TAKES_ARG = {"-o", "--push-option", "--receive-pack", "--exec", "--repo"}
WRAPPERS = {"env", "sudo", "time", "timeout", "stdbuf", "setsid", "ionice", "flock", "nohup", "command", "builtin", "exec", "nice"}
SHELLS = {"bash", "sh", "zsh", "dash"}
KEYWORDS = {"{", "}", "!", "if", "then", "else", "elif", "do", "while", "until", "fi", "done"}
BUILTINS = {"status", "log", "diff", "add", "commit", "fetch", "pull", "checkout", "branch", "merge", "show", "rev-parse", "worktree", "config", "stash", "clone", "init", "remote", "tag", "reset", "rebase", "restore", "switch"}   # git ignores an alias that shadows one of these
SHELL_C = re.compile(r"-[A-Za-z]*c[A-Za-z]*")       # -c, -lc, -ec, -xc: the next word is a command line
PYTHON = re.compile(r"python[\d.]*")
PYTHON_C = re.compile(r"-[A-Za-z]*c")
OPS = set("();<>|&")
HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_]\w*)\1(?P<rest>[^\n]*)\n(?P<body>.*?)\n[ \t]*\2[ \t]*(?=\n|$)", re.S)
MENTION = re.compile(r"\bgit\b[\s\S]{0,80}?\bpush\b|\bgh\b[\s\S]{0,80}?\b(?:merge|api)\b")       # within 80 characters
UNREADABLE = re.compile(r"\bgit\b.*\bpush\b|\bgh\b.*\b(?:merge|api)\b", re.S)       # for a command that cannot be tokenised: anywhere
LEASE = re.compile(r"--force-with-lease=\S+:[0-9a-f]{40}(?![0-9a-f])")
SHA = re.compile(r"[0-9a-f]{40}")
API_VALUE_LONG = {"--header", "--jq", "--template", "--preview", "--hostname", "--cache"}
# the class of a reason: DENY never passes; FORCE passes with a command verdict for the whole string and a --force-with-lease=<ref>:<sha>; CMD passes with a command verdict for the whole string; FF (a literal 40-hex sha pushed to a protected branch, no + and no force flag) passes when it is the only kind of reason and a go verdict of kind merge has that sha as its head
DENY, FORCE, CMD, FF = "deny", "force", "cmd", "ff"
MCP_TOOLS = {"merge_pull_request", "push_files", "create_or_update_file", "delete_file"}
VIA_PR = "merge through a PR"
PROTECTED = frozenset()     # set from the configuration by _configure()
VERDICTS = None             # the verdict file, set by _configure()


def _configure(cfg=None):
    """Takes the protected branches and the verdict file from the project's configuration (loop.json over the defaults)."""
    global PROTECTED, VERDICTS
    cfg = config.load() if cfg is None else cfg
    protected = cfg["protected_branches"]
    PROTECTED = frozenset([protected] if isinstance(protected, str) else protected)
    VERDICTS = cfg.path("verdicts")


def git_out(wd, *a):
    try: return subprocess.run(["git", "-C", wd, *a], capture_output=True, text=True, timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError): return ""

def bash_lines(cmd):
    """cmd with its # comments dropped and then its backslash-newlines joined, as bash reads them (see the module docstring)."""
    out, ctx, i, prev = [], [""], 0, " "
    while i < len(cmd):
        c, q = cmd[i], ctx[-1]
        if q == "'":
            if c == "'": ctx.pop()
        elif c == "\\":
            if cmd[i + 1:i + 2] != "\n": out.append(cmd[i:i + 2]); prev = "a"
            i += 2; continue
        elif q in ('"', "`") and c == q: ctx.pop()
        elif c == "$" and cmd[i + 1:i + 2] == "(": ctx.append("$)"); out.append("$("); prev = "("; i += 2; continue
        elif q in ("", ")", "$)"):
            if c == "#" and prev in " \t\n;&|()<>":
                j = cmd.find("\n", i); i = len(cmd) if j < 0 else j; continue
            if c in "'\"`": ctx.append(c)
            elif c == "(": ctx.append(")")
            elif c == ")" and q: ctx.pop(); out.append(c); prev = "a" if q == "$)" else ")"; i += 1; continue      # after the ) of a $(...) the word goes on
        elif q == '"' and c == "`": ctx.append(c)
        out.append(c); prev = c; i += 1
    return "".join(out)

def substitutions(cmd):
    """The text of each $(...) in cmd (nested ones too) and of each `...` pair, each read twice: once counting every parenthesis, once skipping quoted or escaped ones."""
    out = [m.group(1) for m in re.finditer(r"`([^`]*)`", cmd)]
    for m in re.finditer(r"\$\(", cmd):
        for quoted in (False, True):
            n, i, q = 1, m.end(), ""
            while i < len(cmd) and n:
                c = cmd[i]
                if quoted and c == "\\" and q != "'": i += 2; continue
                if quoted and q: q = "" if c == q else q
                elif quoted and c in "'\"": q = c
                else: n += {"(": 1, ")": -1}.get(c, 0)
                i += 1
            out.append(cmd[m.end():i - 1] if not n else cmd[m.end():])
    return list(dict.fromkeys(out))

def simple_commands(cmd):
    """Token lists of the simple commands of a shell command line (heredoc bodies removed, # comments dropped as bash drops them, quotes honoured)."""
    cmd = bash_lines(HEREDOC.sub(r"\g<rest>", cmd)).replace("\n", " ;\n; ")
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=True); lex.whitespace_split = True; lex.commenters = ""      # bash_lines has dropped the comments: a # left is text
    out, cur = [], []
    for t in lex:
        if t and all(c in OPS for c in t):
            if cur: out.append(cur); cur = []
        else: cur.append(t)
    if cur: out.append(cur)
    return out

def branch_and_upstream(wd):
    br = git_out(wd, "symbolic-ref", "-q", "--short", "HEAD"); up = git_out(wd, "config", "--get", f"branch.{br}.merge") if br else ""
    return br, (up[len("refs/heads/"):] if up.startswith("refs/heads/") else up)

def default_remote(wd, br):
    """The remote `git push` uses when none is named: branch.<b>.pushRemote, then remote.pushDefault, then branch.<b>.remote, then origin."""
    for key in ((f"branch.{br}.pushRemote",) if br else ()) + ("remote.pushDefault",) + ((f"branch.{br}.remote",) if br else ()):
        v = git_out(wd, "config", "--get", key)
        if v: return v
    return "origin"

def risky_flag(name):
    """DENY, FORCE or None for a long option: git accepts any unambiguous prefix of a long option, so a prefix of a risky one is treated as that option."""
    if len(name) <= 2: return None
    if name.startswith("--force"): return FORCE
    hits = [r for r in LONG if r.startswith(name)]
    return None if not hits else DENY if hits[0] in DENY_LONG else FORCE

def refspec_reasons(r):
    """[(class, why)] for one refspec (as written, or as configured in remote.<name>.push); [] when it is plain. HEAD and @ are handled by the caller."""
    if re.search(r"[$`]", r): return [(DENY, f"refspec {r} cannot be read")]
    out = []
    if r.startswith("+"): out.append((FORCE, f"forced refspec {r}")); r = r[1:]
    if "*" in r: return out + [(DENY, f"wildcard refspec {r} can reach a protected branch")]
    src, dst = r.split(":", 1) if ":" in r else (r, r)
    if not src: out.append((FORCE, f"delete refspec {r}"))
    d = dst[len("refs/heads/"):] if dst.startswith("refs/heads/") else dst
    if d in PROTECTED: out.append((FF, f"push of {src} to {d}") if SHA.fullmatch(src) and not out else (DENY, f"destination {d}: {VIA_PR}, or push the 40-hex head that a merge verdict names"))
    return out

def push_reasons(args, wd):
    """[(class, why)] for a `git push` with these arguments (the words after push); [] when it can go on."""
    why, pos, i = [], [], 0
    while i < len(args):
        a = args[i]
        if a in TAKES_ARG: i += 2; continue
        if a.startswith("--"):
            c = risky_flag(a.split("=", 1)[0])
            if c: why.append((c, f"flag {a}"))
        elif a.startswith("-") and len(a) > 1:
            if re.fullmatch(r"-[A-Za-z0-9]+", a) and set(a[1:]) & set("fd"): why.append((FORCE, f"flag {a}"))
        else: pos.append(a)
        i += 1
    refspecs, br_up = pos[1:], None
    if not refspecs:                  # git decides the destination from the repository's configuration
        br, up = br_up = branch_and_upstream(wd); remote = pos[0] if pos else default_remote(wd, br)
        refspecs = [l for l in git_out(wd, "config", "--get-all", f"remote.{remote}.push").split("\n") if l]
        if git_out(wd, "config", "--bool", "--get", f"remote.{remote}.mirror") == "true": why.append((DENY, f"remote {remote} is configured as a mirror"))
        if not refspecs and git_out(wd, "config", "--get", "push.default") == "matching": why.append((DENY, "push.default is matching: every branch of the same name is sent"))
    implied = not refspecs
    for r in refspecs:
        if r in ("HEAD", "@"): implied = True; continue
        why += refspec_reasons(r)
    if implied:
        br, up = br_up or branch_and_upstream(wd)
        if br in PROTECTED: why.append((DENY, f"implied destination: the current branch is {br}: {VIA_PR}"))
        elif up in PROTECTED: why.append((DENY, f"implied destination: the current branch {br} tracks {up}: {VIA_PR}"))
    return why

def api_write(args):
    """True when the arguments of a `gh api` call write (a missing method value counts as a write)."""
    i = 0
    while i < len(args):
        a = args[i]; i += 1
        if a.startswith("--"):
            name, eq, val = a.partition("=")
            if name in ("--field", "--raw-field", "--input"): return True
            if name == "--method":
                if (val if eq else (args[i] if i < len(args) else "")).upper() != "GET": return True
            if not eq and (name == "--method" or name in API_VALUE_LONG): i += 1
        elif a.startswith("-") and len(a) > 1:
            for n, ch in enumerate(a[1:], 2):          # -i takes no value; every other short flag of gh api does, as the rest of the word or as the next word
                if ch == "i": continue
                if ch in "fF": return True
                rest = a[n:].lstrip("=")
                if ch == "X" and (rest or (args[i] if i < len(args) else "")).upper() != "GET": return True
                if not a[n:]: i += 1
                break
    return False

def gh_reasons(args):
    """[(class, why)] for a gh command (the words after gh)."""
    words = [a for a in args if not a.startswith("-")]; sub = words[0] if words else ""
    if sub == "pr" and "merge" in words[1:3]: return [(DENY, f"gh pr merge: {VIA_PR}")]
    if sub == "repo" and "edit" in words[1:3]: return [(CMD, "gh repo edit")]
    if sub == "api" and api_write(args): return [(CMD, "gh api write")]
    return []

def analyse(cmd, wd, depth=0):
    """[(class, why)] for a shell command line run in folder wd; [] when none."""
    if depth: cmd = cmd.replace(" ;\n; ", "\n")      # a body taken from a word of the outer line gets its own newlines back
    why = []
    if any(MENTION.search(m["body"]) for m in HEREDOC.finditer(cmd)): why.append((DENY, "a heredoc body mentions git push or gh merge/api: run it as its own command"))
    if depth < 2: why += [r for s in substitutions(HEREDOC.sub("", cmd)) for r in decide(s, wd, depth + 1)]
    for toks in simple_commands(cmd):
        for n, t in enumerate(toks):                   # `git push ...` inside backticks
            if t.startswith("`") and depth < 2:
                inner = [t.lstrip("`")] + toks[n + 1:]; inner[-1] = inner[-1].rstrip("`"); why += analyse(" ".join(inner), wd, depth + 1)
        wrapped = False
        while toks and (re.fullmatch(r"\w+=.*", toks[0]) or toks[0].rsplit("/", 1)[-1] in WRAPPERS or toks[0] in KEYWORDS): toks = toks[1:]; wrapped = True
        if not toks: continue
        if wrapped:                                    # env -i git push, sudo -u x git push, nice -n 5 git push: the command word follows the wrapper's own arguments
            for n, t in enumerate(toks):
                if t in SHELLS or t in ("git", "gh", "eval", "xargs", "cd") or PYTHON.fullmatch(t): toks = toks[n:]; break
            else: toks = next((toks[n:] for n, t in enumerate(toks) if t.rsplit("/", 1)[-1] in SHELLS | {"git", "gh"}), toks)
        head = toks[0].rsplit("/", 1)[-1]              # tools/git is git
        if head == "cd" and len(toks) > 1 and not re.search(r"[$`]", toks[1]): wd = os.path.normpath(os.path.join(wd, os.path.expanduser(toks[1]))); continue
        if head == "eval" and depth < 2: why += analyse(" ".join(toks[1:]), wd, depth + 1); continue
        if head == "xargs":                            # the arguments of the push come from stdin: unreadable
            rest = toks[1:]
            if "git" in rest and "push" in rest[rest.index("git"):]: why.append((DENY, "xargs supplies the arguments of a git push"))
            if "gh" in rest:
                sub = rest[rest.index("gh") + 1:]; why += gh_reasons(sub)
                if "api" in sub: why.append((CMD, "xargs supplies the arguments of a gh api call"))
            continue
        if head in SHELLS and depth < 2:
            k = next((n for n, t in enumerate(toks) if n and SHELL_C.fullmatch(t)), None)
            if k is not None:         # the command line is the first word after the option cluster; any later word is looked at too
                for t in toks[k + 1:]:
                    if not t.startswith("-"): why += analyse(t, wd, depth + 1)
                continue
        if PYTHON.fullmatch(head):                     # python -c BODY: the body is a program, which the parser does not read
            k = next((n for n, t in enumerate(toks) if n and PYTHON_C.fullmatch(t)), None)
            if k is not None and MENTION.search(re.sub(r"(?: ;)*\n(?:; )*", "\n", " ".join(toks[k + 1:]))): why.append((DENY, "a python -c body mentions git push or gh merge/api: run it as its own command"))
            continue
        if head == "gh": why += gh_reasons(toks[1:]); continue
        if head != "git": continue
        j, w2, aliases = 1, wd, {}
        while j < len(toks) and toks[j].startswith("-"):
            if toks[j] == "-C" and j + 1 < len(toks): w2 = os.path.normpath(os.path.join(w2, os.path.expanduser(toks[j + 1]))); j += 2
            elif toks[j] == "-c" and j + 1 < len(toks):
                key, _, val = toks[j + 1].partition("=")
                if key.startswith("alias."): aliases[key[len("alias."):]] = val
                j += 2
            elif toks[j] in ("--git-dir", "--work-tree", "--namespace", "--exec-path") and j + 1 < len(toks): j += 2
            else: j += 1
        if j >= len(toks): continue
        name, rest = toks[j], toks[j + 1:]
        if name == "push": why += push_reasons(rest, w2); continue
        alias = aliases.get(name) or (git_out(w2, "config", "--get", f"alias.{name}") if depth < 2 and name not in BUILTINS and re.fullmatch(r"[\w-]+", name) else "")
        if alias: why += analyse((alias[1:] if alias.startswith("!") else "git " + alias) + " " + shlex.join(rest), w2, depth + 1)
    return why

def decide(cmd, wd, depth=0):
    """analyse(), with a command that cannot be tokenised and mentions git push or gh merge/api counted as a reason."""
    try: return analyse(cmd, wd, depth)
    except ValueError: return [(DENY, "the command cannot be read")] if UNREADABLE.search(cmd) else []

def read_verdicts():
    """The verdicts that count: verdict "go", id, by, answer and undo present, not withdrawn. A missing file is no verdicts; a file that cannot be read raises."""
    try:
        with open(VERDICTS, encoding="utf-8") as f: lines = f.read().splitlines()
    except FileNotFoundError: return []
    rows = []
    for l in lines:
        try: r = json.loads(l)
        except ValueError: continue
        if isinstance(r, dict): rows.append(r)
    withdrawn = {r.get("of") for r in rows if r.get("verdict") == "withdrawn"}
    full = lambda r: all(isinstance(r.get(k), str) and r[k].strip() for k in ("id", "by", "answer", "undo"))
    return [r for r in rows if r.get("verdict") == "go" and full(r) and r["id"] not in withdrawn]

def judge_bash(cmd, wd):
    """The reason to deny a Bash command line; "" when it may go on."""
    why = decide(cmd, wd)
    if not why: return ""
    said = lambda cs: "; ".join(dict.fromkeys(t for c, t in why if c in cs))
    if any(c == DENY for c, _ in why): return said((DENY,)) + (f"; also {said((FORCE, CMD, FF))}" if any(c != DENY for c, _ in why) else "")
    if any(c == FF for c, _ in why):
        if any(c != FF for c, _ in why): return said((FORCE, CMD)) + f": a push to a protected branch goes alone, with no force, delete or gh write in the same command ({said((FF,))})"
        heads = {str(v.get("head", "")).lower() for v in read_verdicts() if v.get("kind") == "merge"}
        miss = [t for c, t in why if c == FF and SHA.search(t).group() not in heads]
        return f"{miss[0]}: no go verdict of kind merge has this head (record the advisor's verdict before the push)" if miss else ""
    if any(c == FORCE for c, _ in why) and not LEASE.search(cmd): return said((FORCE, CMD)) + ": a force or delete push must carry --force-with-lease=<ref>:<40 hex sha>"
    if any(v.get("kind") == "command" and isinstance(v.get("command"), str) and v["command"].strip() == cmd.strip() for v in read_verdicts()): return ""
    return said((FORCE, CMD)) + ": no command verdict equals this whole command (record the advisor's verdict first, with the command exactly as run)"

def judge_merge(ti):
    repo, pr = f"{ti.get('owner')}/{ti.get('repo')}".lower(), ti.get("pullNumber"); pr = str(int(pr)) if isinstance(pr, (int, float)) and pr == int(pr) else str(pr)
    head = str(ti.get("expectedHeadSha") or "").lower()
    if ti.get("merge_method") != "merge": return 'merge_pull_request needs merge_method "merge" (a squash or rebase would not match the verdict\'s undo)'
    if not SHA.fullmatch(head): return "merge_pull_request needs expectedHeadSha, the 40-hex head the verdict covers"
    mine = [v for v in read_verdicts() if v.get("kind") == "merge" and str(v.get("repo", "")).lower() == repo and str(v.get("pr")) == pr]
    if not mine: return f"no go verdict of kind merge for {repo}#{pr}: record the advisor's verdict before the merge"
    same = [v for v in mine if str(v.get("head", "")).lower() == head]
    if not same: return f"the verdict for {repo}#{pr} covers head {', '.join(str(v.get('head'))[:7] for v in mine)}, the call says {head[:7]}: the head moved, or the wrong sha was passed"
    if not any(v["id"] in str(ti.get("commit_message") or "") for v in same): return f"commit_message must contain the verdict id ({same[-1]['id']})"
    return ""

def judge_branch_write(tool, ti):
    br = ti.get("branch")
    if not isinstance(br, str) or not br.strip(): return f"{tool} without a branch writes to the default branch: name a branch other than the protected ones"
    b = br.strip(); b = b[len("refs/heads/"):] if b.startswith("refs/heads/") else b
    return f"{tool} on {b}: {VIA_PR}" if b in PROTECTED else ""

def judge(name, ti, wd):
    """The reason to deny a tool call; "" when it may go on."""
    _configure()
    short = name.rsplit("__", 1)[-1] if name.startswith("mcp__") else name
    if short == "Bash":
        cmd = ti.get("command")
        return judge_bash(cmd, wd) if isinstance(cmd, str) and ("git" in cmd or "gh" in cmd) else ""
    if short == "merge_pull_request": return judge_merge(ti)
    if short in MCP_TOOLS: return judge_branch_write(short, ti)
    return ""

def artifact_reason(ti):
    """'delete' or 'force' when an Artifact call asks the principal; '' when it passes silently."""
    if ti.get("action") in ("delete", "delete_asset"): return "delete"
    return "force" if ti.get("force") is True else ""

def _emit(decision, reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision, "permissionDecisionReason": reason}}))

def pre(stream):
    """The PreToolUse hook: judges the payload read from `stream`; prints a deny or an ask as the hook protocol says, or nothing. Returns the exit code."""
    text = stream.read()
    if not text.strip():
        print("guard pre: the hook input is empty; the call was not checked", file=sys.stderr); return 0
    try: d = json.loads(text)
    except ValueError:
        print("guard pre: the hook input is not JSON; the call was not checked", file=sys.stderr); return 0
    d = d if isinstance(d, dict) else {}
    ti = d.get("tool_input") if isinstance(d.get("tool_input"), dict) else {}
    name = d.get("tool_name") if isinstance(d.get("tool_name"), str) else "Bash" if "command" in ti else ""
    if name == "Artifact":
        why = artifact_reason(ti)
        if why: _emit("ask", f"Artifact {why} is the principal's call")
        return 0
    try: why = judge(name, ti, d.get("cwd") or os.getcwd())
    except (Exception, SystemExit) as e:          # fail closed for a call that mentions push, merge or api
        if name.rsplit("__", 1)[-1] in MCP_TOOLS or re.search(r"push|merge|api|repo\s+edit", str(ti.get("command"))):
            why = f"the guard failed ({type(e).__name__}: {str(e)[:100]}) on a call that mentions push, merge or api"
        else:
            print(f"guard pre: the check failed on a call that does not mention push, merge or api ({type(e).__name__}: {str(e)[:100]}); the call was not checked", file=sys.stderr)
            return 1
    if why: _emit("deny", "guard: " + why)
    return 0

PLAIN = re.compile(r"[A-Za-z][\w-]*(\(.+\))?")

def blanket(rule):
    """True for an allow rule that grants a whole family: a bare Bash, Bash(*) or Bash(:*), an MCP server as a whole, or every tool of one server."""
    return bool(re.fullmatch(r"Bash(\([\s:*]*\))?", rule)) or (rule.startswith("mcp__") and ("__" not in rule[5:] or rule.endswith("*")))

def check_rules(rules):
    """Raises ValueError when the rules are not an object of lists of plain rule strings (and of retired entries with a reason), an allow or deny rule is a blanket, or a retired or deny rule is also listed under allow or ask."""
    if not isinstance(rules, dict): raise ValueError("the rules file is not a JSON object")
    for k in ("allow", "ask", "deny"):
        if not isinstance(rules.get(k, []), list): raise ValueError(f"{k} is not a list")
        for r in rules.get(k, []):
            if not isinstance(r, str) or not PLAIN.fullmatch(r): raise ValueError(f"{k}: {r!r} is not a plain rule string")
    bad = [r for k in ("allow", "deny") for r in rules.get(k, []) if blanket(r)]
    if bad: raise ValueError(f"allow or deny: blanket rules {bad}")
    if not isinstance(rules.get("retired", []), list): raise ValueError("retired is not a list")
    for e in rules.get("retired", []):
        if not isinstance(e, dict) or not isinstance(e.get("rule"), str) or not PLAIN.fullmatch(e["rule"]): raise ValueError(f"retired: {e!r} is not an object with a plain rule string")
        if not isinstance(e.get("reason"), str) or not e["reason"].strip(): raise ValueError(f"retired: {e['rule']!r} has no reason")
    retired = [e["rule"] for e in rules.get("retired", [])]
    lists = {k: rules.get(k, []) for k in ("allow", "ask", "deny")}
    clash = sorted({r for r in retired + lists["deny"] if r in lists["allow"] or r in lists["ask"]})
    if clash: raise ValueError(f"a retired or deny rule is also listed under allow or ask: {clash}")
    if len(set(retired)) != len(retired): raise ValueError("retired lists a rule twice")

def load_rules(path):
    """The rules of a rules file, checked; raises OSError or ValueError."""
    rules = json.loads(pathlib.Path(path).read_text(encoding="utf-8")); check_rules(rules); return rules

def merge_rules(settings, rules):
    """Applies the rules to the settings dict in place; returns (allow added, ask added, moved from allow to ask, retired rules removed from ask, deny added)."""
    p = settings.setdefault("permissions", {}); allow, ask, deny = list(p.get("allow", [])), list(p.get("ask", [])), list(p.get("deny", []))
    retired = set() if os.environ.get("PERMISSIONS_KEEP_RETIRED") else {e["rule"] for e in rules.get("retired", [])}   # a caller sets it when the guard that replaces these asks is not installed
    gone = [r for r in ask if r in retired]; ask = [r for r in ask if r not in retired]       # exactly the retired rules, from ask only
    add_deny = [r for r in rules.get("deny", []) if r not in deny]; deny += add_deny
    add_ask = [r for r in rules.get("ask", []) if r not in ask]; ask += add_ask
    moved = [r for r in allow if r in ask]; allow = [r for r in allow if r not in ask]
    add_allow = [r for r in rules.get("allow", []) if r not in allow and r not in ask]; allow += add_allow
    p["allow"], p["ask"] = allow, ask
    if deny: p["deny"] = deny
    return add_allow, add_ask, moved, gone, add_deny

def apply_rules(rules_file, settings_file=None, check_only=False):
    """Merges the rules file into the user settings file (default ~/.claude/settings.json). Returns the exit code; a refusal writes nothing."""
    path = pathlib.Path(settings_file) if settings_file else pathlib.Path(os.path.expanduser("~/.claude/settings.json"))
    try: rules = load_rules(rules_file)
    except (OSError, ValueError) as e:
        print(f"- permissions: no usable rules ({type(e).__name__}: {str(e)[:150]}); nothing written", file=sys.stderr); return 1
    try: settings = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except ValueError as e:
        print(f"- permissions: {path} is not valid JSON ({e}); left as it is", file=sys.stderr); return 1
    if not isinstance(settings, dict):
        print(f"- permissions: {path} is not a JSON object; left as it is", file=sys.stderr); return 1
    a, k, m, g, d = merge_rules(settings, rules)
    print(f"- permissions ({rules_file}): {len(a)} allow and {len(k)} ask rules " + ("would be added" if check_only else "added") + f", {len(m)} moved from allow to ask, {len(g)} retired ask rules " + ("would be removed" if check_only else "removed") + f", {len(d)} deny rules " + ("would be added" if check_only else "added") + ("; nothing written" if check_only else "") + f" in {path}")
    if check_only or not (a or k or m or g or d): return 0
    path.parent.mkdir(parents=True, exist_ok=True); fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f: json.dump(settings, f, indent=2, ensure_ascii=False); f.write("\n")
        json.loads(pathlib.Path(tmp).read_text(encoding="utf-8")); os.replace(tmp, path)
    except (OSError, ValueError) as e:
        try: os.unlink(tmp)
        except OSError: pass
        print(f"- permissions: the write failed ({type(e).__name__}: {str(e)[:150]}); {path} left as it was", file=sys.stderr); return 1
    return 0

class _Text:
    """Standard input that was already read, handed to pre as a stream."""
    def __init__(self, text): self.text = text
    def read(self): return self.text


def main(argv=None):
    """The guard verb: `pre` (the hook) or `permissions apply`. Returns the exit code."""
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(prog="loop guard", description="refuse a guarded act without a recorded verdict; merge a permission rules file")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pre", help="the PreToolUse hook: reads the payload on standard input")
    perm = sub.add_parser("permissions", help="permission rules")
    psub = perm.add_subparsers(dest="action", required=True)
    pa = psub.add_parser("apply", help="merge a rules file into a user settings file")
    pa.add_argument("--rules", required=True, help="the rules file (JSON)")
    pa.add_argument("--settings", help="the user settings file (default ~/.claude/settings.json)")
    pa.add_argument("--check", action="store_true", help="say what would change; write nothing")
    try: args = ap.parse_args(argv)
    except SystemExit as e: return e.code if isinstance(e.code, int) else 2
    if args.cmd == "pre":
        text = sys.stdin.read()
        try:   # a user-level hook fires for every session on the machine: a session that works outside this project is not ours to guard
            d, cfg = json.loads(text or "null"), config.load()
            cmd = (d.get("tool_input") or {}).get("command") if isinstance(d, dict) and isinstance(d.get("tool_input"), dict) else ""
            if not cfg.serves(d) and str(cfg.root) not in str(cmd or ""): return 0   # ours all the same when the command names the project
        except (Exception, SystemExit): pass   # undecided here: pre itself decides, and denies where it must
        return pre(_Text(text))
    return apply_rules(args.rules, args.settings, args.check)


if __name__ == "__main__": sys.exit(main())
