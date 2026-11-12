"""Read the emu verdict's coverage; no evaluator code is imported.

INVARIANT: this adapter preserves the engine's existing coverage wording.
FAILS WHEN: an engine layer is omitted without being named as unobserved.
"""
import re

EMU_LAYERS = ("smoke", "chain")
NOT_YET = re.compile(r"^not in the verdict yet: (.*) (?:is|are) not in this loop\s*$", re.M)


def accepts(run):
    """The existing emu CLI or its verdict module."""
    return any(a.endswith("emu") and b == "verdict" for a, b in zip(run, run[1:])) or any(w.endswith("verdict.py") for w in run)


def pass_note(layers, text):
    m = NOT_YET.search(text)
    if m is None:
        return "not run: unknown, the verdict did not say what it leaves out"
    yet = [re.sub(r"\s*\([^)]*\)", "", part).strip() for part in re.split(r" and ", m.group(1))]
    gone = [n for n in EMU_LAYERS if n not in layers] + [n for n in yet if n]
    return ("not run: " + ", ".join(gone)) if gone else "all layers ran"
