#!/usr/bin/env python3
"""md_audit — screen-by-screen audit of a markdown note for a reader who will not wait.

The reader model is the drunken-emu one, transferred from React artifacts to prose:
a phone screen shows about seven sentences; the reader may stop at any screen; nothing
outside the current screen can be assumed remembered (working memory N = 1 screen).
So every check is computed PER SCREEN and the report says which screens fail.

Checks (each a proxy for one clause of the project's readability contract):
  bare_id_units     units where a code/identifier (NEED-0034, COR-0012, arXiv id, md5 prefix,
                    file path, section sign) appears with fewer than MIN_PLAIN plain words
                    around it -> the code carries the meaning alone (zero-lookup violation)
  demonstratives    'this / that / it / 前者 / 后者 / 该 …' at unit start -> referent lives on
                    another screen (zero-ambiguity risk)
  unexpanded_acr    3+ letter capitalised tokens that never appear next to a '(' anywhere in
                    the file (never expanded even once)
  meta_phrases      writing-process words in the body ('this round', '本轮', 'snapshot' …);
                    expected in ledgers (--kind ledger), a defect in notes (--kind note)
  first_screen_verdict  the first screen carries an action/verdict marker
  dead_local_links  markdown links to paths that do not exist relative to the file
Usage:
  python3 md_audit.py FILE.md [--kind note|ledger] [--screen 7] [--json]
Exit code 0 always; this is an audit, not a gate. Numbers are proxies; the report names the
screen so a human can read it and overrule.
"""
import re, sys, os, json

ID_PATTERNS = [r'\bNEED-\d{4}\b', r'\bCOR-\d{4}\b', r'\bCLAIM-\d{4}\b', r'\bobs\.? ?\d{2,3}\b',
               r'\bP-[A-Z0-9]{1,4}\b', r'\b\d{4}\.\d{4,5}\b', r'\b[0-9a-f]{7,32}…?\b', r'§ ?\d', r'\bC\d(\([iv]+\))?\b',
               r'`[^`]+\.(md|tsv|py|txt|json|tex)`', r'\bR-\d+\b', r'\bE\d\b']
ID_RE = re.compile('|'.join(ID_PATTERNS))
DEMO_RE = re.compile(r'^(this|that|these|those|it|its|the former|the latter|here|there|该|此|其|它|前者|后者|上述|以上|这|那)\b', re.I)
ACR_RE = re.compile(r'\b[A-Z][A-Z0-9]{2,}\b')
ACR_SKIP = {'FACT','JUDGMENT','SPECULATIVE','PENDING','TL','DR','URL','PDF','HTML','JSON','TSV','CSV','README','MD','CI','API','TODO','NOTE','OK','ISBN','DOI','ID','IDS','ETC','ARXIV','GITHUB','SIG','CI'}
META_DEFAULT = ['this round', 'this session', 'this instance', 'the instance', '本轮', '本 session', '落盘', 'tool call', 'snapshot', 'budget', 'commit', 'md5', 'read back', '预算']
VERDICT_RE = re.compile(r'你需要|需要你|verdict|判决|TL;DR|conclusion|the one action|first sentence|决定|结论|answer', re.I)
LINK_RE = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]+|[\u4e00-\u9fff]{1,4}")

def units(text):
    """Split into reading units: sentences, table rows, list items. Code fences are one unit each."""
    out=[]; fence=False; buf=[]
    for line in text.split('\n'):
        s=line.strip()
        if s.startswith('```'):
            fence = not fence
            if not fence: out.append('```' + ' '.join(buf)[:200]); buf=[]
            continue
        if fence: buf.append(s); continue
        if not s: continue
        if s.startswith('|') or s.startswith('#') or re.match(r'^[-*] |^\d+\. ', s):
            out.append(s); continue
        for sent in re.split(r'(?<=[.!?。！？])\s+', s):
            if sent.strip(): out.append(sent.strip())
    return out

def plain_words(u):
    u2 = ID_RE.sub(' ', u); u2 = re.sub(r'https?://\S+', ' ', u2)
    return WORD_RE.findall(u2)

def audit(path, kind='note', screen=7, min_plain=6, meta=None):
    text = open(path, encoding='utf-8', errors='replace').read()
    meta = meta or META_DEFAULT
    us = units(text)
    screens = [us[i:i+screen] for i in range(0, len(us), screen)] or [[]]
    expanded_acrs = set(m.group(0) for m in ACR_RE.finditer(text) if re.search(re.escape(m.group(0)) + r'\s*\(|\(\s*' + re.escape(m.group(0)), text))
    # emphasis, not acronym: the same word occurs in lower/title case somewhere in the file
    lowers = set(w.lower() for w in re.findall(r'[A-Za-z]+', text) if not w.isupper())
    def acr_candidates(u):
        u2 = re.sub(r'`[^`]*`', ' ', u)                      # code spans (file names, ids)
        u2 = re.sub(r'\b[A-Z0-9]+(?:-[A-Z0-9]+)+\b', ' ', u2) # hyphenated caps chains = file names / ids
        u2 = ID_RE.sub(' ', u2)
        return [a for a in ACR_RE.findall(u2) if a not in ACR_SKIP and a not in expanded_acrs
                and a.lower() not in lowers and not re.match(r'^[0-9A-F]+$', a)]
    rep = {'file': path, 'kind': kind, 'units': len(us), 'screens': len(screens),
           'words': len(WORD_RE.findall(text)), 'screens_failing': {}, 'totals': {}}
    tot = {'bare_id_units':0,'demonstratives':0,'unexpanded_acr':0,'meta_phrases':0,'dead_local_links':0}
    low = text.lower()
    for k in meta:
        tot['meta_phrases'] += low.count(k.lower())
    base = os.path.dirname(os.path.abspath(path))
    dead=[]
    for m in LINK_RE.finditer(text):
        tgt = m.group(1).split('#')[0]
        if tgt and not tgt.startswith(('http','mailto')) and not os.path.exists(os.path.join(base, tgt)): dead.append(tgt)
    tot['dead_local_links'] = len(dead)
    for si, scr in enumerate(screens, 1):
        f = {}
        bare = [u for u in scr if ID_RE.search(u) and len(plain_words(u)) < min_plain and not u.startswith(('|','```','#'))]
        demo = [u for u in scr if DEMO_RE.match(u)]
        acrs = sorted({a for u in scr for a in acr_candidates(u)})
        if bare: f['bare_id_units'] = [u[:90] for u in bare]
        if demo: f['demonstratives'] = [u[:60] for u in demo]
        if acrs: f['unexpanded_acr'] = acrs
        tot['bare_id_units'] += len(bare); tot['demonstratives'] += len(demo); tot['unexpanded_acr'] += len(acrs)
        if f: rep['screens_failing'][si] = f
    rep['first_screen_verdict'] = bool(VERDICT_RE.search(' '.join(screens[0]))) if screens[0] else False
    rep['dead_local_links_list'] = dead[:10]
    rep['totals'] = tot
    rep['load'] = {'human_minutes_at_200wpm': round(rep['words']/200, 1), 'ai_tokens_est': int(rep['words']*1.35)}
    return rep

def summary_line(r):
    t = r['totals']
    return (f"{os.path.basename(r['file']):<48} {r['words']:>6}w {r['screens']:>4}scr  bareID={t['bare_id_units']:<3} demo={t['demonstratives']:<3} "
            f"acr={t['unexpanded_acr']:<3} meta={t['meta_phrases']:<3} deadlinks={t['dead_local_links']:<2} verdict1st={'Y' if r['first_screen_verdict'] else 'N'}")

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    kind = 'ledger' if '--kind' in sys.argv and sys.argv[sys.argv.index('--kind')+1] == 'ledger' else 'note'
    scr = int(sys.argv[sys.argv.index('--screen')+1]) if '--screen' in sys.argv else 7
    out = [audit(p, kind, scr) for p in args if p.endswith(('.md',))]
    if '--json' in sys.argv: print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        for r in out:
            print(summary_line(r))
            if '--verbose' in sys.argv:
                for si, f in list(r['screens_failing'].items())[:8]:
                    print(f"   screen {si}: {json.dumps(f, ensure_ascii=False)[:300]}")
