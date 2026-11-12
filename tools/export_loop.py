#!/usr/bin/env python3
"""Export the existing loop runtime without instance state or engine dependencies.

Usage: python3 tools/export_loop.py DESTINATION
       python3 tools/export_loop.py --verify DESTINATION

The destination must not exist. File bytes and executable modes are preserved.
The manifest identifies exported bytes, their Git HEAD match, and exclusions;
it is an inventory, not a signature or a claim that tests passed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "MANIFEST.json"
README = """# Standalone loop runtime

This is a byte-preserving export of the session harness in drunken-emu.
Start with `python3 -I bin/loop doctor` or the runnable instance in
`examples/loop-minimal/README.md`. The full manual is `loop/README.md`.

The engine is supplied by each instance as an executable check; the sample
checks a JSON contract. The browser engine, its vendor bundles, repository
history, tests, user settings and instance state are not included. Original
LICENSE, NOTICE and THIRD_PARTY_NOTICES.md are retained; the vendor references
in those notices describe the source repository, not bundled runtime dependencies.
The emu-specific coverage reader remains in the source checkout; this export
uses the generic check protocol without inferring coverage from a command's name.

Python standard library and git suffice for the sample on Linux. Hooks and
transcript handling target Claude Code; backup requires bash 4, GNU tools and
flock. The optional `loop/mod/` is a Claude host adapter, not installed here.
No hook installation, backup remote, or semantic correctness is implied.

`MANIFEST.json` records SHA-256 hashes, modes and Git provenance. Verify with
`python3 tools/export_loop.py --verify .`. Verification checks inventoried files,
not extra files created by use. Preserve the manifest separately if authenticity
matters: it is not signed. No timestamp or machine-specific source path is emitted.
"""


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True,
                          capture_output=True).stdout


def sources():
    """Explicit runtime boundary; never traverse state, .git, settings or caches."""
    names = ["bin/loop", "LICENSE", "NOTICE", "THIRD_PARTY_NOTICES.md", "tools/export_loop.py"]
    names += [p.relative_to(ROOT).as_posix() for p in (ROOT / "loop").iterdir()
              if p.suffix in (".py", ".sh") or p.name == "README.md"]
    # Host adapter files are selected from Git, not an unbounded worktree crawl.
    tracked = git("ls-files", "-z", "loop/mod").decode().split("\0")
    names += [p for p in tracked if p and not p.endswith(".test.ts")]
    # The general runtime needs the dispatcher, not the source checkout's
    # subject-specific readers. Instances may install their own readers later.
    names += ["loop/adapters/__init__.py"]
    names += ["examples/loop-minimal/" + n for n in
              ("README.md", "loop.json", "check.py", "artifact.json", "policy.json")]
    # The manual's linked evidence is required: absence must fail the export,
    # rather than silently ship a package with a broken validation pointer.
    names += ["docs/HARNESS-EXTRACTION.md", "docs/HARNESS-VALIDATION.md",
              "docs/HARNESS-HISTORY.md", "docs/EMU-LOOP-RETIRED.md"]
    return sorted(set(names))


def export(destination):
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"destination already exists: {destination}")
    if not destination.parent.is_dir():
        raise ValueError("destination parent must exist")
    head = git("rev-parse", "HEAD").decode().strip()
    records = {}
    with tempfile.TemporaryDirectory(prefix=".loop-export-", dir=destination.parent) as temp:
        stage = Path(temp) / "package"
        stage.mkdir()
        for name in sources():
            source, target = ROOT / name, stage / name
            if source.is_symlink() or not source.is_file():
                raise ValueError(f"runtime source must be a regular file: {name}")
            data = source.read_bytes()
            # Preserve executable semantics, independent of the checkout umask.
            mode = 0o755 if source.stat().st_mode & stat.S_IXUSR else 0o644
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            target.chmod(mode)
            try:
                matches = git("show", f"{head}:{name}") == data
            except subprocess.CalledProcessError:
                matches = False
            records[name] = {"sha256": digest(data), "mode": oct(mode), "matches_head": matches}
        (stage / "README.md").write_text(README, encoding="utf-8")
        (stage / "README.md").chmod(0o644)
        records["README.md"] = {"sha256": digest(README.encode()), "mode": "0o644", "generated": True}
        manifest = {"format": 1, "source_head": head, "files": records,
                    "scope": "loop runtime, optional host adapter, generic instance scaffold",
                    "excluded": [".git", "user settings", "instance state", "browser engine", "tests", "vendor bundles",
                                 "subject-specific report readers"],
                    "verification": "inventory only; no test or semantic correctness claim"}
        (stage / MANIFEST).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        # mkdir reserves the destination exclusively; a race cannot overwrite it.
        destination.mkdir()
        try:
            for child in stage.iterdir():
                shutil.move(str(child), str(destination / child.name))
        except BaseException:
            shutil.rmtree(destination)
            raise
    return manifest


def verify(destination):
    root = Path(destination).resolve()
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    failures = []
    for name, rec in manifest["files"].items():
        path = root / name
        if Path(name).is_absolute() or ".." in Path(name).parts:
            failures.append(f"invalid path: {name}")
            continue
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
            failures.append(f"missing or nonregular: {name}")
        elif digest(path.read_bytes()) != rec["sha256"]:
            failures.append(f"bytes changed: {name}")
        elif stat.S_IMODE(path.stat().st_mode) != int(rec["mode"], 8):
            failures.append(f"mode changed: {name}")
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("destination")
    args = parser.parse_args()
    try:
        if args.verify:
            failures = verify(args.destination)
            print("\n".join(failures) if failures else "inventory verified")
            return 1 if failures else 0
        manifest = export(args.destination)
        print(f"exported {len(manifest['files'])} files; source HEAD {manifest['source_head']}")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(2, f"export-loop: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
