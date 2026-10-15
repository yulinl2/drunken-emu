# CLAUDE.md — session bootstrap for drunken-emu

**Session start, with no instruction needed.** Follow the README's own "Fresh session?" order (`README.md`, top): `docs/OPEN-PROBLEMS.md` → README's `## Falsified` section → `docs/SANDBOX-FACTS.md` → `docs/EXPLORE-SPEC.md`. The SessionStart hook (`.claude/settings.json`) prints that order from the README. If the list here and the README ever differ, the README is the source.

**This kit is standalone.** It is infrastructure, separate from the content lines that use it, and a session needs nothing from outside this repository to start: the order above, the hook and the four documents it names are all in this tree, and no step in this file requires reading another repository (P-6e35, updated 2026-10-15: the owner, the kit is fully standalone, an infra thing apart from the content line).

**Role.** The cold-reader kit: it renders a claude.ai single-file React artifact in headless Chromium and audits it the way an impatient first-time reader would. `checks/svg_legibility.py` audits static SVG figures the same way (rendered type size, label overlap, ink outside the viewBox).
