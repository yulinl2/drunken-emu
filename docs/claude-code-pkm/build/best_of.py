#!/usr/bin/env python3
"""Pick one winner for each group of overlapping nodes, and demote the rest.

Usage, from the repository root:

    python3 docs/claude-code-pkm/build/best_of.py            write src/24-best-of.txt
    python3 docs/claude-code-pkm/build/best_of.py --verify   count groups left among active nodes

Two active nodes overlap when they share a surface family and a normalized
title, and their bodies say the same thing: a word-set Jaccard similarity of at
least 0.5, or an overlap coefficient of at least 0.8 when the shorter body has
four or more content words. Overlapping nodes form a group. Inside a group the
winner is the first node in this order, and nothing is merged or averaged:

  1. a body that is not a placeholder ("Row of the ... page." and
     "Section of the ... page." are placeholders)
  2. VERIFIED status
  3. the longer body, which carries more information
  4. the shorter id, which is the first emitted form without a page or number suffix
  5. the id in alphabetical order

Each other node in the group becomes SUPERSEDED. A pointer to the winner goes
before its old body, and the old body is kept: demote, do not destroy.
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_NAME = "24-best-of.txt"

spec = importlib.util.spec_from_file_location("build_nodes", os.path.join(HERE, "build_nodes.py"))
bn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bn)

SKIP_KINDS = {"source", "tag", "decision", "question", "gap", "observation",
              "session-rule", "injected", "environment", "precedence"}
INACTIVE = {"SUPERSEDED", "REMOVED", "DECIDED", "DEFINED", "GAP"}
FAMILY = {"hook": "hook", "hook-field": "hook", "hook-rule": "hook",
          "plugin": "plugin", "plugin-field": "plugin",
          "skill": "skill", "skill-field": "skill"}
STOP = {"a", "an", "and", "are", "as", "at", "be", "by", "each", "for", "from", "if", "in",
        "is", "it", "its", "of", "on", "or", "that", "the", "their", "this", "to", "when",
        "with", "your"}
PLACEHOLDER = re.compile(r"^(Row|Section) of the .* page\.$")


def title_key(title):
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def words(body):
    return {w for w in re.findall(r"[a-z0-9]+", body.lower()) if w not in STOP}


def overlaps(a, b):
    wa, wb = words(a["body"]), words(b["body"])
    shared = len(wa & wb)
    if not shared:
        return False
    jaccard = shared / len(wa | wb)
    coefficient = shared / min(len(wa), len(wb))
    return jaccard >= 0.5 or (coefficient >= 0.8 and min(len(wa), len(wb)) >= 4)


def groups(by_id):
    """Return the overlap groups (lists of two or more nodes) among active nodes."""
    buckets = {}
    for node in by_id.values():
        if node["kind"] in SKIP_KINDS or node["status"] in INACTIVE:
            continue
        key = (FAMILY.get(node["kind"], node["kind"]), title_key(node["title"]))
        if key[1]:
            buckets.setdefault(key, []).append(node)
    found = []
    for members in buckets.values():
        if len(members) < 2:
            continue
        parent = {m["id"]: m["id"] for m in members}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for i, a in enumerate(members):
            for b in members[i + 1:]:
                if overlaps(a, b):
                    parent[find(a["id"])] = find(b["id"])
        components = {}
        for m in members:
            components.setdefault(find(m["id"]), []).append(m)
        found.extend(c for c in components.values() if len(c) > 1)
    return sorted(found, key=lambda g: min(m["id"] for m in g))


def winner_of(group):
    def rank(node):
        return (bool(PLACEHOLDER.match(node["body"])), node["status"] != "VERIFIED",
                -len(node["body"]), len(node["id"]), node["id"])
    return min(group, key=rank)


def replace_row(loser, winner):
    sources = ", ".join(loser["sources"]) or "-"
    body = "Superseded by [[" + winner["id"] + "]]. " + " ".join(loser["body"].split())
    return ("replace " + loser["id"] + " | " + loser["kind"] + " | SUPERSEDED | " + sources
            + " | " + loser["title"] + " | " + body)


def main():
    if "--verify" in sys.argv:
        errors = []
        by_id, _ = bn.build(errors)
        if errors:
            for message in errors:
                print("ERROR:", message, file=sys.stderr)
            return 1
        left = groups(by_id)
        print("overlap groups left among active nodes:", len(left))
        return 0 if not left else 1

    errors = []
    by_id, _ = bn.build(errors, skip={OUT_NAME})
    if errors:
        for message in errors:
            print("ERROR:", message, file=sys.stderr)
        print(str(len(errors)) + " problem(s); nothing written", file=sys.stderr)
        return 1

    found = groups(by_id)
    rows, shown = [], []
    for group in found:
        winner = winner_of(group)
        losers = sorted((m for m in group if m is not winner), key=lambda m: m["id"])
        for loser in losers:
            rows.append(replace_row(loser, winner))
        shown.append((winner["title"], winner["id"], [m["id"] for m in losers]))

    dec = ("dec.d15 | decision | DECIDED | - | Overlapping candidates: one winner per group | "
           "Groups: " + str(len(found)) + "; winners kept: " + str(len(found))
           + "; losers demoted to SUPERSEDED: " + str(len(rows)) + ". "
           "Two active nodes overlap when they share a surface family and a normalized title, and their "
           "bodies say the same thing (word Jaccard similarity of at least 0.5, or an overlap coefficient of "
           "at least 0.8 with four or more content words). The winner is the first in this order: a body "
           "that is not a placeholder, VERIFIED status, the longer body, the shorter id, then the alphabetically "
           "first id. A loser keeps its old body after a pointer to the winner: demote, do not destroy. Nothing "
           "is merged or averaged. A hand-written node and a generated row with the same id are not a group: the "
           "hand-written node stays, because it is curated and cites a source. Check: build/best_of.py --verify "
           "reports zero groups among active nodes.")
    header = [
        "# GENERATED by build/best_of.py on 2026-10-22: the replace rows demote the losers of each overlap group. Do not edit.",
        dec,
    ]
    path = os.path.join(HERE, "src", OUT_NAME)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(header + rows) + "\n")

    print("overlap groups:", len(found), "| losers demoted:", len(rows))
    for title, winner_id, loser_ids in shown[:12]:
        print("  %-28s keep %-44s demote %s" % (title[:28], winner_id[:44], ", ".join(loser_ids)[:70]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
