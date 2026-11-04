"""What a build reads from a speeds-kit checkout, recorded in docs/predictions/hw2-sample-pass.inputs.json.

The checkout is read, never written (no `git` command here changes anything; reads use --no-optional-locks), and it may be moved or deleted
afterwards: every later step reads the committed inputs file and the committed measured files, not the checkout.  The inputs file holds the
commit, the sha256 of every file that was read, and, for every code construct a note cites, its place in the script (cites.py).
"""
from __future__ import annotations

import datetime
import hashlib
import json
import re
import subprocess
from pathlib import Path

from . import cites

SCHEMA = "emu-prediction-inputs/1"
REPO = Path(__file__).resolve().parents[2]
INPUTS_PATH = "docs/predictions/hw2-sample-pass.inputs.json"
MOCK = "tests/tapgrade/mock_canvas.py"
DOCS = (cites.TAPGRADE_MD, cites.RUNBOOK)
READ = (cites.SCRIPT, MOCK, cites.TAPGRADE_PY, cites.PICKS_PY) + DOCS


class InputsError(RuntimeError):
    pass


def sha256(data: bytes | str) -> str:
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode("utf-8")).hexdigest()


def git(root: Path, *args: str) -> str | None:
    """one read-only git command in the checkout; None when git or the repository is not there"""
    try:
        p = subprocess.run(["git", "--no-optional-locks", "-C", str(root), *args], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return p.stdout.strip() if p.returncode == 0 else None


def now_et() -> str:
    """'2026-10-05 00:41 EDT': the zone is the label of the zone, never a guess from a number"""
    try:
        from zoneinfo import ZoneInfo
        t = datetime.datetime.now(ZoneInfo("America/New_York"))
        return f"{t:%Y-%m-%d %H:%M} {t.tzname()}"
    except Exception:                                   # no tz database: October is EDT, UTC-4 (the label is checked by the reader of the date)
        t = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4)))
        return f"{t:%Y-%m-%d %H:%M} EDT"


def read_files(root: Path) -> dict[str, bytes]:
    out = {}
    for rel in READ:
        p = root / rel
        if not p.is_file():
            raise InputsError(f"{rel} is not in {root}: this is not a speeds-kit checkout with the sample mode (0.6.7 or later)")
        out[rel] = p.read_bytes()
    return out


def texts(files: dict[str, bytes]) -> dict[str, str]:
    return {k: v.decode("utf-8") for k, v in files.items()}


def make(root: Path, commit: str | None = None, drafted: str | None = None) -> dict:
    """the inputs of a build, from a speeds-kit checkout.  `commit`: the commit the files are of (default: the last commit that touched a file read)"""
    root = Path(root)
    files = read_files(root)
    head = git(root, "rev-parse", "HEAD")
    if commit is None:
        commit = git(root, "log", "-1", "--format=%H", "--", *READ)
        if not commit:
            raise InputsError(f"{root} is not a git checkout (or git is missing): say which commit the files are of with --speeds-kit-commit")
        if git(root, "status", "--porcelain", "--", *READ):
            raise InputsError(f"the checkout has local changes in files the registration reads ({', '.join(READ)}): the sha256 would not be a commit's")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise InputsError(f"the commit must be the full 40-character hash, not {commit!r}")
    tx = texts(files)
    script = tx[cites.SCRIPT]
    ver, build = re.search(r'const VERSION = "([^"]+)"', script), re.search(r'const BUILD = "([^"]+)"', script)
    if not ver:
        raise InputsError("no `const VERSION` in the script")
    table = cites.resolve(tx)                           # stops, naming the citation, when a construct a note cites is gone or appears twice
    # the last commit (at or before `commit`) that changed each file read: when only the docs changed in the snapshot's own commit, the code is as of an earlier one and the text says so
    last = {rel: git(root, "log", "-1", "--format=%H", commit, "--", rel) for rel in READ}
    return {
        "schema": SCHEMA,
        "drafted": drafted or now_et(),
        "speeds_kit": {
            "repository": "speeds-kit", "commit": commit, "checkout_head": head, "branch": git(root, "branch", "--show-current"),
            "script": {"path": cites.SCRIPT, "sha256": sha256(files[cites.SCRIPT]), "bytes": len(files[cites.SCRIPT]), "lines": len(script.splitlines()),
                       "version": ver.group(1), "build": build.group(1) if build else None},
            "mock_canvas": {"path": MOCK, "sha256": sha256(files[MOCK])},
            "read": {rel: sha256(files[rel]) for rel in READ if rel not in (cites.SCRIPT, MOCK)},
            "last_changed_by": {rel: c for rel, c in last.items() if c},
        },
        "citations": table,
    }


def load(repo: Path = REPO) -> dict:
    d = json.loads((Path(repo) / INPUTS_PATH).read_text(encoding="utf-8"))
    if d.get("schema") != SCHEMA:
        raise InputsError(f"{INPUTS_PATH}: schema {d.get('schema')!r}, expected {SCHEMA!r}")
    return d


def dump(inputs: dict) -> str:
    return json.dumps(inputs, indent=1, ensure_ascii=False) + "\n"


def problems(inputs: dict, root: Path) -> list[str]:
    """differences between the committed inputs and a checkout: empty means the checkout is what the registration was built from"""
    files = read_files(Path(root))
    sk, out = inputs["speeds_kit"], []
    if sha256(files[cites.SCRIPT]) != sk["script"]["sha256"]:
        out.append(f"{cites.SCRIPT}: sha256 is {sha256(files[cites.SCRIPT])[:12]}..., the inputs say {sk['script']['sha256'][:12]}...")
    if sha256(files[MOCK]) != sk["mock_canvas"]["sha256"]:
        out.append(f"{MOCK}: sha256 changed")
    for rel, want in sk["read"].items():
        if sha256(files[rel]) != want:
            out.append(f"{rel}: sha256 changed")
    return out + cites.verify(inputs["citations"], texts(files))
