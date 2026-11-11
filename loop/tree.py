"""The project's tree, read in one place: load(cfg) returns the whole tree, or raises Refused and names every fault in it.

INVARIANT: a tree is read in one place and is returned whole or refused whole, and the reader writes nothing.
FAILS WHEN: a repeated id or a malformed node reaches a consumer, a refused tree returns a partial result, or a load writes a file.

The file is the one that the configuration key "tree" names. Its top level is an object with a roots list. A node is an object
with a string id and an optional children list, and every other field of a node is handed on unchanged. An id is one node.
A node with no title or no status is not refused here: a later check judges it. Standard library only.
"""
import collections
import json
import pathlib

Tree = collections.namedtuple("Tree", ["nodes", "paths"])


class Refused(Exception):
    """The tree cannot be returned whole. kind is "missing", "unreadable" or "malformed"; path is the absolute path of the file;
    detail is the reader's error text (unreadable), the faults joined by "; " (malformed), or "" (missing)."""

    def __init__(self, kind, path, detail, shown):
        self.kind, self.path, self.detail = kind, path, detail
        if kind == "missing":
            text = "no tree at " + shown
        elif kind == "unreadable":
            text = "tree at " + shown + " is not readable"
        else:
            text = "tree at " + shown + " is malformed: " + detail
        super().__init__(text)


def _shown(path, root):
    """The path as the configuration writes it: relative to the project root when it lies under it (as the gate's _rel does)."""
    try:
        return str(pathlib.Path(path).relative_to(root))
    except ValueError:
        return str(path)


def load(cfg):
    """The whole tree of the project, or Refused when it cannot be returned whole. It reads the file at every call."""
    path = cfg.path("tree")
    shown = _shown(path, cfg.root)
    if not path.is_file():
        raise Refused("missing", path, "", shown)
    try:
        top = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise Refused("unreadable", path, str(exc), shown)
    if not isinstance(top, dict) or not isinstance(top.get("roots"), list):
        raise Refused("malformed", path, "the top level is not an object with a roots list", shown)
    # an iterative walk in pre-order: a node is visited before its children, and siblings in file order
    faults, where, nodes, paths = [], {}, {}, {}
    stack = [(node, pos, None, []) for pos, node in reversed(list(enumerate(top["roots"])))]
    while stack:
        node, pos, parent_loc, parent_ids = stack.pop()
        ident = node.get("id") if isinstance(node, dict) else None
        step = (ident if isinstance(ident, str) else "?") + "[" + str(pos) + "]"
        loc = step if parent_loc is None else parent_loc + " > " + step
        if not isinstance(node, dict):
            faults.append(loc + ": not an object")
            continue
        if isinstance(ident, str):
            ids = None if parent_ids is None else parent_ids + [ident]
            where.setdefault(ident, []).append(loc)
            nodes.setdefault(ident, node)
            paths.setdefault(ident, ids)
        else:
            faults.append(loc + ": no string id")
            ids = None
        if "children" in node:
            kids = node["children"]
            if not isinstance(kids, list):
                faults.append(loc + ": children is not a list")
            else:
                stack.extend((kid, k, loc, ids) for k, kid in reversed(list(enumerate(kids))))
    twice = ["id " + ident + " occurs more than once (an id is one node): " + ", ".join(locs)
             for ident, locs in where.items() if len(locs) > 1]
    if faults or twice:
        raise Refused("malformed", path, "; ".join(faults + twice), shown)
    return Tree(nodes, paths)
