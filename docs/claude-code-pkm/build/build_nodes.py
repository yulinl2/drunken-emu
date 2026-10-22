#!/usr/bin/env python3
"""Build one Markdown node per concept, plus an index, from build/src/*.txt.

Source lines are read in file-name order. Blank lines and lines starting with
'#' are ignored. Two forms define a node.

Row: one line, six fields split on ' | ' (the body keeps any later ' | '):

    <id> | <kind> | <status> | <sources> | <title> | <body>

    replace <id> | <kind> | <status> | <sources> | <title> | <body>

A row that starts with 'replace ' overrides the node with that id: kind, status,
sources, title and body are replaced, so the node keeps its id and its links.
best_of.py uses it to demote the losers of an overlap group.

Block: for bodies that need several lines:

    @node <id>
    kind: <kind>
    status: <status>
    sources: <S-numbers, or ->
    title: <title>
    body:
    <markdown, blank lines allowed>
    @end

Rules:
  id       lowercase letters, digits, '.' and '-'; unique across all files.
  sources  comma-separated S-numbers such as S6, S8; '-' for none.
           S6 links to the node src.s6.
  body     [[id]] links to another node; each one becomes a Markdown link.

Writes nodes/<id>.md for every node and INDEX.md, one level above build/.
Nothing is written if any line is malformed or any link or source dangles.

    python3 build_nodes.py           write the nodes and INDEX.md
    python3 build_nodes.py --check   write nothing; exit 1 if any file is out of date
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(HERE, "src")
ROOT = os.path.dirname(HERE)
NODE_DIR = os.path.join(ROOT, "nodes")
INDEX_PATH = os.path.join(ROOT, "INDEX.md")

KINDS = {
    "source": "Sources",
    "tag": "Legend tags",
    "decision": "Decisions",
    "question": "Open questions",
    "term": "Glossary",
    "hook": "Hook events",
    "hook-rule": "Hook rules",
    "observation": "Repo observations",
    "setting": "Settings",
    "setting-file": "Settings files",
    "precedence": "Precedence",
    "permission-mode": "Permission modes",
    "permission-rule": "Permission rules",
    "memory": "Memory",
    "tool": "Tools",
    "skill": "Skills",
    "command": "Slash commands",
    "cli": "CLI subcommands",
    "cli-form": "CLI invocation forms",
    "flag": "CLI flags",
    "env": "Environment variables",
    "plugin": "Plugins",
    "mod": "Mods",
    "mcp": "MCP",
    "feature": "Features",
    "agent-type": "Agent types",
    "process": "Processes",
    "git-rule": "Git and PR rules",
    "injected": "Injected context",
    "environment": "Environment classes",
    "gap": "Coverage gaps",
    "session-rule": "Session rules",
    "shortcut": "Keyboard shortcuts",
    "agent-field": "Subagent fields",
    "skill-field": "Skill fields",
    "hook-field": "Hook input and output fields",
    "plugin-field": "Plugin and marketplace fields",
    "output-style": "Output styles",
    "statusline-field": "Status line fields",
}
STATUSES = {"VERIFIED", "INDEX", "SESSION", "REPO", "UNVERIFIED", "OPEN",
            "DEFINED", "DECIDED", "SUPERSEDED", "REMOVED", "GAP"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9.\-]*$")
LINK_RE = re.compile(r"\[\[([^\[\]]+)\]\]")
SOURCE_RE = re.compile(r"^S(\d+)$")


def finish(node, errors):
    """Validate one parsed node and return it in its final shape."""
    where, nid, meta = node["where"], node["id"], node["meta"]
    if not ID_RE.match(nid):
        errors.append(f"{where}: bad id '{nid}'")
    for key in ("kind", "status", "title"):
        if not meta.get(key):
            errors.append(f"{where}: '{nid}' has no {key}")
    if meta.get("kind") and meta["kind"] not in KINDS:
        errors.append(f"{where}: '{nid}' has unknown kind '{meta['kind']}'")
    if meta.get("status") and meta["status"] not in STATUSES:
        errors.append(f"{where}: '{nid}' has unknown status '{meta['status']}'")
    sources = []
    raw = meta.get("sources") or "-"
    if raw != "-":
        for token in (t.strip() for t in raw.split(",")):
            if SOURCE_RE.match(token):
                sources.append(token)
            else:
                errors.append(f"{where}: '{nid}' has bad source '{token}'")
    body = "\n".join(node["body"]).strip("\n")
    return {"id": nid, "where": where, "kind": meta.get("kind", ""),
            "status": meta.get("status", ""), "title": meta.get("title", nid),
            "sources": sources, "body": body}


def parse(path, errors):
    """Read one source file and return its finished nodes."""
    name = os.path.basename(path)
    nodes, block = [], None
    with open(path, encoding="utf-8") as fh:
        for number, raw in enumerate(fh, 1):
            line = raw.rstrip("\n")
            where = f"{name}:{number}"
            if block is not None:
                if line.strip() == "@end":
                    nodes.append(finish(block, errors))
                    block = None
                elif block["in_body"]:
                    block["body"].append(line)
                elif line.strip() == "body:":
                    block["in_body"] = True
                elif line.strip():
                    key, sep, value = line.partition(":")
                    if sep:
                        block["meta"][key.strip()] = value.strip()
                    else:
                        errors.append(f"{where}: expected 'key: value' inside @node")
                continue
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            if text.startswith("@node "):
                block = {"id": text[len("@node "):].strip(), "where": where,
                         "meta": {}, "body": [], "in_body": False}
                continue
            replace = text.startswith("replace ")
            row = line.lstrip()[len("replace "):] if replace else line
            fields = row.split(" | ", 5)
            if len(fields) != 6:
                errors.append(f"{where}: a row needs six fields split on ' | '")
                continue
            nid, kind, status, sources, title, body = (f.strip() for f in fields)
            node = finish({"id": nid, "where": where,
                           "meta": {"kind": kind, "status": status,
                                    "sources": sources, "title": title},
                           "body": [body]}, errors)
            node["replace"] = replace
            nodes.append(node)
    if block is not None:
        errors.append(f"{name}: @node {block['id']} is never closed with @end")
    return nodes


def build(errors, skip=()):
    """Parse every source file and resolve links, sources and backlinks.

    skip names source files to leave out. best_of.py skips its own output so
    that it recomputes overlap groups from the base lists.
    """
    nodes = []
    for name in sorted(os.listdir(SRC_DIR)):
        if name.endswith(".txt") and name not in skip:
            nodes.extend(parse(os.path.join(SRC_DIR, name), errors))
    overrides = [node for node in nodes if node.get("replace")]
    by_id = {}
    for node in nodes:
        if node.get("replace"):
            continue
        if node["id"] in by_id:
            errors.append(f"{node['where']}: duplicate id '{node['id']}'")
        by_id[node["id"]] = node
    for node in overrides:
        target = by_id.get(node["id"])
        if target is None:
            errors.append(f"{node['where']}: replace target '{node['id']}' does not exist")
            continue
        for key in ("kind", "status", "title", "sources", "body"):
            target[key] = node[key]
    for node in by_id.values():
        node["out"] = []
        for target in LINK_RE.findall(node["body"]):
            if target in by_id:
                node["out"].append(target)
            else:
                errors.append(f"{node['where']}: [[{target}]] in '{node['id']}' is not a node")
        for source in node["sources"]:
            sid = "src." + source.lower()
            if sid in by_id:
                node["out"].append(sid)
            else:
                errors.append(f"{node['where']}: '{node['id']}' cites {source}, but {sid} is missing")
    backlinks = {nid: set() for nid in by_id}
    for node in by_id.values():
        for target in node["out"]:
            backlinks[target].add(node["id"])
    return by_id, backlinks


def quote(text):
    """Return text as a double-quoted YAML scalar."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_node(node, by_id, backlinks):
    """Return the Markdown for one node page."""
    body = LINK_RE.sub(lambda m: f"[{by_id[m.group(1)]['title']}]({m.group(1)}.md)", node["body"])
    head = ["---", f"id: {node['id']}", f"kind: {node['kind']}",
            f"status: {node['status']}", f"title: {quote(node['title'])}"]
    if node["sources"]:
        head.append("sources: [" + ", ".join(node["sources"]) + "]")
    head.append("---")
    lines = head + ["", f"# {node['title']}", ""]
    if node["sources"]:
        cites = ", ".join(f"[{s}]({'src.' + s.lower()}.md)" for s in node["sources"])
        lines += [f"**Sources:** {cites}", ""]
    lines += [body, ""]
    if backlinks:
        lines += ["## Linked from", ""]
        for bid in sorted(backlinks, key=lambda b: (by_id[b]["title"].lower(), b)):
            lines.append(f"- [{by_id[bid]['title']}]({bid}.md)")
        lines.append("")
    return "\n".join(lines)


def summary(node, by_id):
    """One-line plain-text summary of a node, for the index."""
    first = node["body"].split("\n", 1)[0]
    text = LINK_RE.sub(lambda m: by_id[m.group(1)]["title"], first)
    text = text.replace("**", "").strip()
    return text if len(text) <= 160 else text[:157].rsplit(" ", 1)[0] + "..."


def render_index(by_id):
    """Return the index page: counts by kind, then one line per node."""
    counts = {}
    for node in by_id.values():
        counts[node["kind"]] = counts.get(node["kind"], 0) + 1
    lines = ["# Claude Code PKM: node index", "",
             "Generated by `build/build_nodes.py` from `build/src/*.txt`. "
             "Edit those files and rebuild; do not edit this page.", "",
             f"{len(by_id)} nodes.", "",
             "| Kind | Nodes |", "| --- | ---: |"]
    for kind, label in KINDS.items():
        if counts.get(kind):
            lines.append(f"| {label} (`{kind}`) | {counts[kind]} |")
    lines.append("")
    for kind, label in KINDS.items():
        members = sorted((n for n in by_id.values() if n["kind"] == kind),
                         key=lambda n: n["id"])
        if not members:
            continue
        lines += [f"## {label}", ""]
        for node in members:
            lines.append(f"- [{node['title']}](nodes/{node['id']}.md) · "
                         f"{node['status']} · {summary(node, by_id)}")
        lines.append("")
    return "\n".join(lines) + "\n"


def stale_files(by_id, backlinks):
    """Return the output paths whose text differs from what the sources produce."""
    expected = {INDEX_PATH: render_index(by_id)}
    for nid, node in by_id.items():
        expected[os.path.join(NODE_DIR, nid + ".md")] = render_node(node, by_id, backlinks[nid])
    stale = []
    for path, text in expected.items():
        try:
            with open(path, encoding="utf-8") as fh:
                current = fh.read()
        except FileNotFoundError:
            current = None
        if current != text:
            stale.append(path)
    if os.path.isdir(NODE_DIR):
        for name in os.listdir(NODE_DIR):
            path = os.path.join(NODE_DIR, name)
            if name.endswith(".md") and path not in expected:
                stale.append(path)
    return stale


def main():
    errors = []
    by_id, backlinks = build(errors)
    if errors:
        for message in errors:
            print("ERROR:", message, file=sys.stderr)
        print(f"{len(errors)} problem(s); nothing written", file=sys.stderr)
        return 1
    if "--check" in sys.argv:
        stale = stale_files(by_id, backlinks)
        for path in stale:
            print("STALE:", os.path.relpath(path, ROOT), file=sys.stderr)
        if stale:
            print(f"{len(stale)} file(s) out of date; run build_nodes.py", file=sys.stderr)
            return 1
        print(f"{len(by_id)} nodes and INDEX.md match the sources")
        return 0
    os.makedirs(NODE_DIR, exist_ok=True)
    for name in os.listdir(NODE_DIR):
        if name.endswith(".md"):
            os.remove(os.path.join(NODE_DIR, name))
    for nid, node in by_id.items():
        with open(os.path.join(NODE_DIR, nid + ".md"), "w", encoding="utf-8") as fh:
            fh.write(render_node(node, by_id, backlinks[nid]))
    with open(INDEX_PATH, "w", encoding="utf-8") as fh:
        fh.write(render_index(by_id))
    print(f"wrote {len(by_id)} nodes to {NODE_DIR} and {INDEX_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
