"""Optional report readers; the harness contract remains exit code plus JSON.

INVARIANT: a generic checker need not name an engine or import one.
FAILS WHEN: a generic report is treated as complete coverage without evidence.
"""
import importlib
import pkgutil


def readers():
    """Discover installed report readers in module-name order.

    A reader supplies accepts(argv) and pass_note(layers, text). The source
    checkout may carry subject-specific readers; the generic export carries
    only this dispatcher, so arbitrary checker names imply no subject coverage.
    """
    for info in sorted(pkgutil.iter_modules(__path__, __name__ + "."), key=lambda item: item.name):
        module = importlib.import_module(info.name)
        if callable(getattr(module, "accepts", None)) and callable(getattr(module, "pass_note", None)):
            yield module


def pass_note(run, layers, text):
    """Describe unobserved coverage, using an adapter only for its own report."""
    for reader in readers():
        if reader.accepts(run):
            return reader.pass_note(layers, text)
    return ("coverage beyond reported layers is unknown" if layers
            else "the check reports no layers")
