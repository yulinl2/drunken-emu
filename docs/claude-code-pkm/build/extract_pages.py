#!/usr/bin/env python3
"""Factorize the in-scope Claude Code reference pages into node rows.

Usage, from the repository root:

    python3 docs/claude-code-pkm/build/extract_pages.py PAGES_DIR PAGES_DIR/llms.txt

PAGES_DIR holds <slug>.md for every page in IN_SCOPE, where a slug is the path
under https://code.claude.com/docs/en/ without the .md suffix. The second
argument is the docs index, https://code.claude.com/docs/llms.txt. The download
commands are written into the header of src/19-pages-tables.txt.

Writes three generated source lists, which build_nodes.py turns into nodes:
  src/19-pages-tables.txt    one source row per page, then the table-row concepts
  src/20-pages-headings.txt  the section-heading concepts
  src/22-scope-out.txt       dec.d14: every English docs page out of scope, with a reason

A concept is a table row or a section heading (levels 2 to 4) on an in-scope
page. A candidate whose id already exists in a hand-written source list counts
as already present and keeps its existing node. The script writes nothing if an
in-scope page is missing or is not on the index.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
BASE = "https://code.claude.com/docs/en/"
TODAY = "2026-10-21"
FIRST_SOURCE = 14
GENERATED = {"19-pages-tables.txt", "20-pages-headings.txt", "22-scope-out.txt"}

# slug: (table kind, table id prefix, heading kind, heading id prefix); None skips that part.
IN_SCOPE = {
    "how-claude-code-works": (None, None, "feature", "feature"),
    "features-overview": (None, None, "feature", "feature"),
    "claude-directory": ("feature", "feature", "feature", "feature"),
    "context-window": (None, None, "feature", "feature"),
    "prompt-caching": (None, None, "feature", "feature"),
    "memory": ("memory", "memory", "memory", "memory"),
    "sessions": ("feature", "feature", "feature", "feature"),
    "remote-control": (None, None, "feature", "feature"),
    "code-review-local": ("feature", "feature", "feature", "feature"),
    "ultrareview": ("feature", "feature", "feature", "feature"),
    "agents": (None, None, "feature", "feature"),
    "sub-agents": ("agent-field", "agent-field", "feature", "feature"),
    "agent-view": (None, None, "feature", "feature"),
    "agent-teams": ("feature", "feature", "feature", "feature"),
    "cross-session-messaging": ("feature", "feature", "feature", "feature"),
    "workflows": ("feature", "feature", "feature", "feature"),
    "worktrees": ("feature", "feature", "feature", "feature"),
    "mcp": ("mcp", "mcp", "mcp", "mcp"),
    "skills": ("skill-field", "skill-field", "feature", "feature"),
    "artifacts": (None, None, "feature", "feature"),
    "channels": (None, None, "feature", "feature"),
    "channels-reference": ("feature", "feature", "feature", "feature"),
    "scheduled-tasks": ("feature", "feature", "feature", "feature"),
    "goal": (None, None, "feature", "feature"),
    "headless": ("feature", "feature", "feature", "feature"),
    "deep-links": (None, None, "feature", "feature"),
    "debug-your-config": ("feature", "feature", "feature", "feature"),
    "plugins/overview": (None, None, "plugin", "plugin"),
    "plugins/install": ("plugin", "plugin", "plugin", "plugin"),
    "plugins/code-intelligence": (None, None, "plugin", "plugin"),
    "plugins/security": (None, None, "plugin", "plugin"),
    "plugins/components": ("plugin-field", "plugin-field", "plugin", "plugin"),
    "plugins/dependencies": (None, None, "plugin", "plugin"),
    "plugin-evals": (None, None, "feature", "feature"),
    "plugins/cli-hints": (None, None, "plugin", "plugin"),
    "plugins/loading": ("plugin-field", "plugin-field", "plugin", "plugin"),
    "plugins/manifest-reference": ("plugin-field", "plugin-field", "plugin", "plugin"),
    "plugins/marketplace-reference": ("plugin-field", "plugin-field", "plugin", "plugin"),
    "plugins/cli-reference": ("cli", "cli", "feature", "feature"),
    "plugins/mods/overview": (None, None, "mod", "mod"),
    "plugins/mods/reference": ("mod", "mod", "mod", "mod"),
    "plugins/mods/events": (None, None, "mod", "mod"),
    "plugins/mods/api": (None, None, "mod", "mod"),
    "plugins/mods/interface": (None, None, "mod", "mod"),
    "plugins/mods/admin": (None, None, "mod", "mod"),
    "plugins/org": (None, None, "plugin", "plugin"),
    "plugins/relevance": (None, None, "plugin", "plugin"),
    "managed-settings": ("setting", "setting", "feature", "feature"),
    "server-managed-settings": (None, None, "feature", "feature"),
    "managed-mcp": (None, None, "mcp", "mcp"),
    "auto-mode-config": ("setting", "setting", "feature", "feature"),
    "monitoring-usage": ("feature", "feature", "feature", "feature"),
    "permissions": ("permission-rule", "permission-rule", "permission-rule", "permission-rule"),
    "permission-modes": ("permission-mode", "permission-mode", "permission-mode", "permission-mode"),
    "sandboxing": ("setting", "setting", "feature", "feature"),
    "sandbox-environments": (None, None, "feature", "feature"),
    "model-config": (None, None, "feature", "feature"),
    "fast-mode": (None, None, "feature", "feature"),
    "advisor": (None, None, "feature", "feature"),
    "output-styles": (None, None, "output-style", "output-style"),
    "terminal-config": ("feature", "feature", "feature", "feature"),
    "fullscreen": (None, None, "feature", "feature"),
    "accessibility": (None, None, "feature", "feature"),
    "voice-dictation": (None, None, "feature", "feature"),
    "statusline": ("statusline-field", "statusline-field", "feature", "feature"),
    "keybindings": ("shortcut", "shortcut", "feature", "feature"),
    "commands": ("command", "cmd", "feature", "feature"),
    "env-vars": ("env", "env", None, None),
    "tools-reference": ("tool", "tool", "tool", "tool"),
    "interactive-mode": ("shortcut", "shortcut", "feature", "feature"),
    "checkpointing": (None, None, "feature", "feature"),
    "hooks": ("hook-field", "hook-field", "hook-rule", "hook-rule"),
}

# Per-page table overrides: first header cell (lowercase) -> (kind, prefix), or None to skip.
TABLE_BY_HEADER = {
    "sub-agents": {"agent": ("agent-type", "agent-type"), "field": ("agent-field", "agent-field")},
    "hooks": {"exit code": ("hook-rule", "hook-rule"), "matcher": ("hook-rule", "hook-rule")},
    "env-vars": {"file": None},
}

# Pages factorized by hand before this script existed (in scope under dec.d12, not extracted here).
HAND_SCOPE = {"settings", "settings-reference", "cli-reference", "glossary"}

SKIP_TABLE_HEADERS = {"event", "events"}
BLACK = {
    "example", "examples", "prerequisites", "requirements", "troubleshooting", "next steps",
    "what's next", "see also", "related", "related pages", "overview", "summary", "notes",
    "limitations", "before you begin", "setup", "install", "installation", "usage", "options",
    "configuration", "reference", "introduction", "quickstart", "tips", "best practices",
    "common issues", "learn more", "faq", "common questions", "table of contents", "contents",
    "in this guide", "further reading", "related resources", "try it", "try it out",
}

DESC = re.compile(r"desc|purpose|what|controls|effect|meaning|does|behavior|detail|note|summary", re.I)
HEAD = re.compile(r"^(#{2,4})\s+(.+?)\s*#*\s*$")
HEAD_ANY = re.compile(r"^(#{2,6})\s+(.*\S)\s*$")
LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
LINK_EN = re.compile(r"\]\(https://code\.claude\.com/docs/en/([^)\s]+?)\.md\)")
SEP = re.compile(r"\|[\s:|\-]+\|?")

# Reasons for dec.d14 (out-of-scope English pages).
SURFACE = "surface or integration: where Claude Code runs or what it connects to"
ADMIN = "deployment, enterprise, security, cost or adoption"
GUIDE = "guide or tutorial; its concepts are on the in-scope reference pages"
CATALOGUE = "catalogue of errors, install steps or troubleshooting"
ORIENT = "orientation or release notes"
SDK = "Agent SDK: a separate library; the harness features it uses are on in-scope pages"
DIGEST = "release digest; the features it names are in the command, setting and feature nodes"
LEGAL = "legal text"
NOT_REFERENCE = "not a reference page for a Claude Code feature"

SUB_REASON = {
    "Platforms and integrations": SURFACE,
    "Claude Code in the cloud": SURFACE,
    "Claude Code on desktop": SURFACE,
    "Code review and pull requests": SURFACE,
    "Code Review": SURFACE,
    "Security scans": SURFACE,
    "Run Claude in your own CI": SURFACE,
    "Environments": SURFACE,
    "Self-hosted environments": SURFACE,
    "Setup and access": ADMIN,
    "Deployment": ADMIN,
    "Gateways": ADMIN,
    "Claude apps gateway": ADMIN,
    "Other gateways": ADMIN,
    "Usage and costs": ADMIN,
    "Security and data": ADMIN,
    "Adoption": ADMIN,
    "Guides": GUIDE,
    "Troubleshooting": CATALOGUE,
    "Quickstart": ORIENT,
    "Getting started": ORIENT,
    "Create plugins": GUIDE,
    "Run a marketplace": GUIDE,
    "Agent SDK": SDK,
    "What's New": DIGEST,
    "Resources": LEGAL,
}

OVERRIDE = {
    "settings-example": GUIDE,
    "mcp-quickstart": GUIDE,
    "hooks-guide": GUIDE,
    "common-workflows": GUIDE,
    "prompt-library": GUIDE,
    "best-practices": GUIDE,
    "large-codebases": GUIDE,
    "plugins/create": GUIDE,
    "plugins/publish": GUIDE,
    "plugins/measure": GUIDE,
    "plugins/mods/create": GUIDE,
    "plugins/mods/gallery": GUIDE,
    "plugins/mods/test": GUIDE,
    "plugins/mods/troubleshoot": CATALOGUE,
    "plugins/troubleshooting": CATALOGUE,
    "plugins/create-marketplace": GUIDE,
    "plugins/host-marketplace": GUIDE,
    "plugins/anthropic-marketplaces": "marketplace directory, not a feature reference",
    "troubleshoot-install": CATALOGUE,
    "troubleshooting": CATALOGUE,
    "errors": CATALOGUE,
    "setup": CATALOGUE,
    "overview": ORIENT,
    "quickstart": ORIENT,
    "changelog": ORIENT,
    "auto-mode-classifier-billing": ADMIN,
    "authentication": ADMIN,
    "admin-setup": ADMIN,
    "legal-and-compliance": LEGAL,
}


def clean(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = LINK.sub(r"\1", text)
    return " ".join(text.replace("**", "").replace("__", "").split())


def safe(text):
    return clean(text).replace("|", "/").replace("[[", "[ [")


def slug(text):
    out = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return out[:60].rstrip("-") or "item"


def code_mask(lines):
    mask, inside = [], False
    for line in lines:
        if line.lstrip().startswith(("```", "~~~")):
            mask.append(True)
            inside = not inside
        else:
            mask.append(inside)
    return mask


def split_row(line):
    text = line.strip().replace("\\|", "/")
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|"):
        text = text[:-1]
    return [cell.strip() for cell in text.split("|")]


def tables(lines, mask):
    found, i = [], 0
    while i < len(lines) - 1:
        sep = lines[i + 1].strip()
        is_table = (lines[i].lstrip().startswith("|") and sep.startswith("|")
                    and "-" in sep and SEP.fullmatch(sep) is not None)
        if mask[i] or mask[i + 1] or not is_table:
            i += 1
            continue
        header, rows, j = split_row(lines[i]), [], i + 2
        while j < len(lines) and not mask[j] and lines[j].lstrip().startswith("|"):
            rows.append(split_row(lines[j]))
            j += 1
        found.append((header, rows))
        i = j
    return found


def table_entries(header, rows):
    desc_at = next((k for k, head in enumerate(header) if DESC.search(head)), None)
    out = []
    for cells in rows:
        if not cells or not cells[0]:
            continue
        name = clean(cells[0]).replace("`", "").strip()
        if not re.search(r"[A-Za-z0-9]", name):
            continue
        body = clean(cells[desc_at]) if desc_at is not None and desc_at < len(cells) else ""
        extras = []
        for k, head in enumerate(header):
            if k in (0, desc_at) or k >= len(cells) or not head:
                continue
            value = clean(cells[k])
            if value and value not in ("-", "—", "–"):
                extras.append(clean(head).lower() + ": " + value)
        if extras:
            joined = "; ".join(extras)
            body = body + " (" + joined + ")" if body else joined
        out.append((name, body))
    return out


def first_paragraph(lines, mask, start):
    buf = []
    for j in range(start, len(lines)):
        text = lines[j].strip()
        if mask[j]:
            if buf:
                break
            continue
        if text.startswith("#"):
            break
        if not text:
            if buf:
                break
            continue
        if text.startswith(("|", ">", "<", "{")):
            if buf:
                break
            continue
        buf.append(re.sub(r"^(?:[-*+]|\d+\.)\s+", "", text))
        if len(" ".join(buf)) > 300:
            break
    return safe(" ".join(buf))[:400]


def headings(lines, mask):
    found = []
    for i, line in enumerate(lines):
        match = None if mask[i] else HEAD.match(line)
        if not match:
            continue
        text = clean(match.group(2)).replace("`", "").strip(" :")
        if not re.search(r"[A-Za-z0-9]", text):
            continue
        found.append((text, first_paragraph(lines, mask, i + 1), text.lower() in BLACK))
    return found


def page_title(lines, fallback):
    for line in lines:
        if line.startswith("# "):
            return safe(line[2:]) or fallback
    return fallback


def existing_ids():
    ids = set()
    for name in sorted(os.listdir(SRC)):
        if not name.endswith(".txt") or name in GENERATED:
            continue
        with open(os.path.join(SRC, name), encoding="utf-8") as fh:
            for line in fh:
                match = re.match(r"(?:@node\s+)?([a-z0-9][a-z0-9.\-]*)\s*(?:\||$)", line)
                if match:
                    ids.add(match.group(1))
    return ids


def make_row(prefix, kind, base, label, body, n, slug_name, taken, emitted):
    cid = prefix + "." + slug(base)
    if cid in taken:
        return None, "present"
    if cid in emitted:
        cid = cid + "-" + slug(slug_name)
        k = 2
        while cid in taken or cid in emitted:
            cid = prefix + "." + slug(base) + "-" + slug(slug_name) + "-" + str(k)
            k += 1
    emitted.add(cid)
    row = (cid + " | " + kind + " | VERIFIED | S" + str(n) + " | " + safe(label)
           + " | " + safe(body))
    return row, "new"


def reason_for(slug_name, stack):
    if slug_name in OVERRIDE:
        return OVERRIDE[slug_name]
    for level in sorted(stack, reverse=True):
        if stack[level] in SUB_REASON:
            return SUB_REASON[stack[level]]
    return NOT_REFERENCE


def scope_out(index_path):
    order, reason_of, stack = [], {}, {}
    with open(index_path, encoding="utf-8") as fh:
        for line in fh:
            head = HEAD_ANY.match(line)
            if head:
                level = len(head.group(1))
                stack = {lv: text for lv, text in stack.items() if lv < level}
                stack[level] = head.group(2).strip()
                continue
            for match in LINK_EN.finditer(line):
                slug_name = match.group(1)
                if slug_name not in reason_of:
                    order.append(slug_name)
                    reason_of[slug_name] = reason_for(slug_name, stack)
    return order, reason_of


def write(name, lines):
    with open(os.path.join(SRC, name), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main(pages_dir, index_path):
    missing = [s for s in IN_SCOPE if not os.path.isfile(os.path.join(pages_dir, s + ".md"))]
    if missing:
        print("MISSING pages, nothing written:", ", ".join(missing), file=sys.stderr)
        return 1
    english, reason_of = scope_out(index_path)
    covered = set(IN_SCOPE) | HAND_SCOPE
    not_on_index = sorted(covered - set(english))
    if not_on_index:
        print("In scope but not on the index, nothing written:", ", ".join(not_on_index), file=sys.stderr)
        return 1
    out_slugs = [s for s in english if s not in covered]

    taken = existing_ids()
    emitted = set()
    src_rows, table_rows, head_rows, report = [], [], [], []
    for index, (slug_name, config) in enumerate(IN_SCOPE.items()):
        t_kind, t_prefix, h_kind, h_prefix = config
        n = FIRST_SOURCE + index
        with open(os.path.join(pages_dir, slug_name + ".md"), encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        mask = code_mask(lines)
        title = page_title(lines, slug_name)
        count = {"trows": 0, "tnew": 0, "theads": 0, "hnew": 0, "present": 0, "generic": 0}

        if t_kind or slug_name in TABLE_BY_HEADER:
            for header, rows in tables(lines, mask):
                first = header[0].lower() if header else ""
                if first in SKIP_TABLE_HEADERS:
                    continue
                choice = TABLE_BY_HEADER.get(slug_name, {}).get(first, (t_kind, t_prefix))
                if not choice or not choice[0]:
                    continue
                kind, prefix = choice
                for name, body in table_entries(header, rows):
                    if kind == "env" and not re.fullmatch(r"[A-Z][A-Z0-9_]*", name):
                        continue
                    if kind == "shortcut" and (name.isdigit() or len(name.split()) > 5):
                        continue
                    count["trows"] += 1
                    if kind == "command":
                        label = name.split()[0]
                        base = label.lstrip("/")
                    else:
                        label, base = name, name
                    row, state = make_row(prefix, kind, base, label,
                                          body or "Row of the " + title + " page.",
                                          n, slug_name, taken, emitted)
                    if row:
                        table_rows.append(row)
                        count["tnew"] += 1
                    else:
                        count["present"] += 1

        if h_kind:
            for text, body, generic in headings(lines, mask):
                if generic:
                    count["generic"] += 1
                    continue
                count["theads"] += 1
                row, state = make_row(h_prefix, h_kind, text, text,
                                      body or "Section of the " + title + " page.",
                                      n, slug_name, taken, emitted)
                if row:
                    head_rows.append(row)
                    count["hnew"] += 1
                else:
                    count["present"] += 1

        src_title = safe("S" + str(n) + ": " + title)
        src_rows.append(
            "src.s" + str(n) + " | source | VERIFIED | - | " + src_title
            + " | Official page " + BASE + slug_name + ", fetched " + TODAY
            + " as raw Markdown from its .md address. Read " + str(count["trows"])
            + " table rows and " + str(count["theads"] + count["generic"])
            + " section headings (" + str(count["generic"]) + " generic ones skipped). New concept nodes: "
            + str(count["tnew"] + count["hnew"]) + "; already present: " + str(count["present"]) + "."
        )
        report.append("%-32s rows %4d  headings %4d  new %4d  present %4d" % (
            slug_name, count["trows"], count["theads"], count["tnew"] + count["hnew"], count["present"]))

    groups = {}
    for slug_name in out_slugs:
        groups.setdefault(reason_of[slug_name], []).append(slug_name)
    parts = [reason + ": " + ", ".join(names) for reason, names in groups.items()]
    scope_body = ("Out of scope under dec.d12: " + str(len(out_slugs)) + " English pages. "
                  + "; ".join(parts))
    dec14 = "dec.d14 | decision | DECIDED | - | Out-of-scope pages and why | " + safe(scope_body)

    write("19-pages-tables.txt", [
        "# GENERATED by build/extract_pages.py on 2026-10-21. Do not edit: change the script and rerun it.",
        "# Raw pages: curl -sS -f -o <slug>.md https://code.claude.com/docs/en/<slug>.md for each IN_SCOPE slug",
        "# (create the folder first for a slug with a slash), and curl -sS -f -o llms.txt https://code.claude.com/docs/llms.txt.",
        "# Then: python3 docs/claude-code-pkm/build/extract_pages.py <pages-dir> <pages-dir>/llms.txt",
    ] + src_rows + table_rows)
    write("20-pages-headings.txt", [
        "# GENERATED by build/extract_pages.py on 2026-10-21: section headings of the in-scope pages. Do not edit.",
    ] + head_rows)
    write("22-scope-out.txt", [
        "# GENERATED by build/extract_pages.py on 2026-10-21: the English docs pages out of scope (dec.d12). Do not edit.",
        dec14,
    ])

    for line in report:
        print(line)
    print("English pages on the index: %d | in scope: %d | hand-factorized: %d | out of scope (dec.d14): %d"
          % (len(english), len(IN_SCOPE), len(HAND_SCOPE), len(out_slugs)))
    print("new concept rows: %d (table rows %d, heading rows %d)"
          % (len(table_rows) + len(head_rows), len(table_rows), len(head_rows)))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
