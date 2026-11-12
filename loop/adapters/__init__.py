"""Optional report readers; the harness contract remains exit code plus JSON.

INVARIANT: a generic checker need not name an engine or import one.
FAILS WHEN: a generic report is treated as complete coverage without evidence.
"""
from . import emu


def pass_note(run, layers, text):
    """Describe unobserved coverage, using an adapter only for its own report."""
    if emu.accepts(run):
        return emu.pass_note(layers, text)
    return ("coverage beyond reported layers is unknown" if layers
            else "the check reports no layers")
