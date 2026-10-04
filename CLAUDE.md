# CLAUDE.md — session bootstrap for drunken-emu

**Session start, with no instruction from the owner needed** (the owner, 2026-10-04 09:44 EDT; MetaProof #263): before your first action read MetaProof `ledgers/ROOT-SEED.md`, first screen only, and follow it. It tells you which role you are (your first message, else your title, else your creator or routine, else a vacant supervisor seat, else a per-question worker), where that role talks (MetaProof #208; the `to:<role>` labels), the owner's filter read in place (MetaSci `kb/owner-guidance/RECAP.md`), the clocks, and where live state is regenerated. With a MetaProof checkout beside this repository: `python3 "$(git rev-parse --show-toplevel)/../MetaProof/bin/session_boot.py" --fetch` prints that screen with the live holders (anchored at the repository root, so it also works from a subdirectory); without one, read the file on GitHub. Then this repository's own rules below.

This repository had no bootstrap file of its own until this minimal one was added 2026-09-28 (MetaSci issue #30),
so the owner's standing instructions have somewhere durable to live instead of being pasted by hand each session.
It defers to the README's own onboarding order rather than duplicating it.

1. **Read MetaProof `ledgers/OWNER-POLICY.md` first** — the owner's standing operating instructions across all
   eight repositories, verbatim, append-only.
2. **Then follow the README's own "Fresh session?" order exactly** (`README.md`, top): `docs/OPEN-PROBLEMS.md` →
   `README.md`'s own `## Falsified` section → `docs/SANDBOX-FACTS.md` → `docs/EXPLORE-SPEC.md`. Role: the cold-reader kit —
   renders a claude.ai single-file React artifact in headless Chromium and audits it the way an impatient
   first-time reader would; `checks/svg_legibility.py` is what other lines' `CLAUDE.md` files point to for
   figure legibility.
