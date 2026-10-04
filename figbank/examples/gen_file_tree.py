#!/usr/bin/env python3
"""figbank/examples/gen_file_tree.py — figbank/'s own tracked files, as a tree spec.

The bank visualizing its own toolkit: proof that `tree`/`treelayout.js` (drunken-emu issue #11) works
on something real before being spent on a harder instance (MetaProof's problem tree, MetaSci's claims
graph). Regenerate after adding or removing files under figbank/:

    python3 figbank/examples/gen_file_tree.py
    node figbank/render_svg.js figbank/examples/figbank-file-tree.json figbank/examples/figbank-file-tree.svg --report /tmp/r.json

Sizing (node_w, canvas) is picked once by hand from `bin/figpipe`'s own overflow errors (it reports
the exact px a box or a canvas needed) and is not recomputed here; if a very long filename is ever
added, `bin/figpipe` will say so and this file's constants need a one-line bump, same as any other spec.
"""
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "figbank-file-tree.json")

TREE_OPTS = {"node_w": 195, "node_h": 24, "gap_x": 30, "gap_y": 6, "orientation": "horizontal",
             "color": "meta", "edge_color": "line"}
ORIGIN = {"x": 16, "y": 50}
CANVAS = {"width": 1140, "height": 1270}   # bin/figpipe's overflow error gave the exact px; +margin


def build_nodes():
    paths = sorted(p for p in subprocess.run(["git", "ls-files", "figbank"], cwd=ROOT, capture_output=True,
                                               text=True, check=True).stdout.splitlines() if p)
    is_dir, nodes = set(), {}

    def ensure(path):
        if path in nodes:
            return
        parent = os.path.dirname(path)
        nodes[path] = {"id": path, "parent": parent or None, "label": os.path.basename(path)}
        if parent:
            is_dir.add(parent)
            ensure(parent)

    for p in paths:
        ensure(p)
    return [{"id": nid, "parent": n["parent"], "label": n["label"] + ("/" if nid in is_dir else "")}
            for nid, n in sorted(nodes.items())]


def build_spec():
    nodes = build_nodes()
    return {
        "id": "figbank-file-tree",
        "message": "figbank's own tracked files, as a tree: the bank visualizing its own toolkit, laid out by treelayout.js from nothing but each file's directory.",
        "provenance": {"generated_by": "figbank/examples/gen_file_tree.py", "source": "git ls-files figbank"},
        "canvas": CANVAS,
        "word_budget": 20,
        "must_not_contain": ["…"],
        "title": {"text": "figbank/, as a tree — every tracked file, laid out from its own path.", "x": 16, "y": 12, "w": 750},
        "tree": {"nodes": nodes, "origin": ORIGIN, **TREE_OPTS},
        "acceptance": {
            "must_mention": [["tree", "file", "directory", "structure", "hierarchy", "nested"]],
            "unreadable_max": 2,
            "legibility": {"width": CANVAS["width"], "min_px": 9,
                            "surface": "a reference diagram meant to be read near its native size and scrolled, not shrunk to a text column"},
            "rounds_max": 3,
        },
    }


if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(build_spec(), f, ensure_ascii=False, indent=1)
        f.write("\n")
    n = len(json.load(open(OUT, encoding="utf-8"))["tree"]["nodes"])
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {n} nodes")
