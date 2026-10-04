# CLAUDE.md — session bootstrap for drunken-emu

**Session start, with no instruction needed.** This repository stands on its own: read `README.md`'s "Fresh session?" order (`docs/OPEN-PROBLEMS.md` → README's `## Falsified` → `docs/SANDBOX-FACTS.md` → `docs/EXPLORE-SPEC.md`), then this file's rules below. The SessionStart hook prints that order. Context from the owner's other repositories (MetaProof `ledgers/ROOT-SEED.md`, `ledgers/OWNER-POLICY.md`) is useful when you can reach it; nothing here depends on it (P-6e35; the owner, 2026-10-04: emu is independent while it is exploratory work, and the shared start block is not required here).

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
