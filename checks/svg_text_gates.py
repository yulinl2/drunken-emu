#!/usr/bin/env python3
"""svg_text_gates.py — the bank's text gates, re-implemented on the <text> of an EXTERNAL SVG.

figbank/render_svg.js enforces word budget, forbidden strings, ellipsis and box overflow while it
lays the figure out. An SVG that came from elsewhere (matplotlib, R, a designer) never passed
through that renderer, so the only honest thing available is to read its <text> elements back.
What this does: word count (+ budget), forbidden strings, ellipsis. What it cannot do — no
containers to overflow, no wrap to measure, no notion of running text vs. label — is returned in
NOT_APPLICABLE so bin/figpipe can say so loudly instead of implying a pass.

    python3 checks/svg_text_gates.py FIG.svg [--budget N] [--forbid STR ...]
"""
import argparse, json, re, sys
import xml.etree.ElementTree as ET

NOT_APPLICABLE = [
    "box overflow: an external SVG has no containers, so 'label wider than its box' is undefined",
    "wrap-to-gap: labels were placed by the external tool; nothing here could re-wrap them",
    "running-text vs label split: the bank exempts symbols/names/region titles from the word budget; "
    "here every <text> counts (numeric-only tokens are reported separately)",
    "layout-derived geometry: tick positions, label positions and marks are whatever the tool emitted, "
    "not computed from the spec's data",
    "one-spec-two-surfaces: this SVG cannot be re-rendered for React or another width",
]


def _hidden(el):
    st = el.get('style', '') or ''
    return el.get('display') == 'none' or 'display:none' in st.replace(' ', '') or el.get('visibility') == 'hidden'


def texts(path, hidden=None):
    root = ET.parse(path).getroot()
    out = []
    for el in root.iter():
        if el.tag.split('}')[-1] == 'text':
            t = re.sub(r'\s+', ' ', ''.join(el.itertext())).strip()
            if t and _hidden(el):
                if hidden is not None:
                    hidden.append(t)
            elif t:
                out.append(t)
    return out


def gates(path, budget=None, forbid=()):
    hid = []
    ts = texts(path, hid)
    toks = [w for t in ts for w in t.split()]
    numeric = [w for w in toks if re.fullmatch(r'[−\-+]?[\d.,]+(e[−\-+]?\d+)?%?', w)]
    errors = []
    if not ts:
        errors.append("no <text> elements: the figure's labels are outlines (e.g. matplotlib svg.fonttype=path), "
                      "so no text gate, legibility audit or word count can see them")
    if hid:
        errors.append(f"{len(hid)} hidden <text> element(s) (display:none / visibility:hidden), e.g. {hid[0][:40]!r}: "
                      "no reader sees them, so they are refused rather than counted or ignored")
    if budget is not None and len(toks) > budget:
        errors.append(f"word budget: {len(toks)} words of <text> (numeric tokens included), budget {budget}")
    for t in ts:
        for bad in forbid:
            if bad.lower() in t.lower():
                errors.append(f"forbidden string {bad!r} in text {t[:40]!r}")
        if '…' in t or '...' in t:
            errors.append(f"ellipsis in text {t[:40]!r}")
    return {"n_text": len(ts), "words": len(toks), "words_non_numeric": len(toks) - len(numeric),
            "errors": errors, "not_applicable": NOT_APPLICABLE}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('svg'); ap.add_argument('--budget', type=int); ap.add_argument('--forbid', nargs='*', default=[])
    a = ap.parse_args()
    r = gates(a.svg, a.budget, a.forbid)
    print(json.dumps(r, indent=1, ensure_ascii=False))
    sys.exit(1 if r['errors'] else 0)
