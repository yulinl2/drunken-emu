#!/usr/bin/env python3
"""reader_load — what each kind of reader must actually read, measured from the tree.

Three readers, three read-in sets, three loads:
  fresh-ai   a new session with no context. Read-in set = every path named in code spans
             inside the package entry file (default metascience-loop-handoff/START-HERE.md)
             that exists on disk, plus the ledgers. Load = bytes/words/est. tokens. Failure
             mode measured: DANGLING references — NEED-/COR-/CLAIM-/obs ids cited anywhere in
             the read-in set that resolve to no ledger row.
  chat-user  the principal on a phone. Sees the reply (not on disk) and the files presented
             this round (from PRESENTED.tsv: round \\t path). Load = title + first screen of
             each presented file; flag: first screen has no verdict/action marker.
  maintainer reads only what changed. Load = lines added to ledgers since the previous commit.
Also classifies every file in the workspace into
  accumulate  ledgers and verbatim regions (append-only; must be read incrementally)
  bury        raw retrievals (stripped full texts, JSON, VERBATIM/EXTRACTS): deep-dive on demand,
              never in the mandatory read-in
  generate    derived views that say so in their header (regenerate, never read as source)
  deliver     everything else (notes for a reader)
and asserts the property the loop relies on: read-in(fresh-ai) ∩ bury = ∅.
Usage: python3 reader_load.py [--root DIR, default the working directory] [--entry PATH] [--json]
"""
import os, re, sys, json, subprocess
ROOT = sys.argv[sys.argv.index('--root')+1] if '--root' in sys.argv else os.environ.get("EMU_ROOT", os.getcwd())
ENTRY = sys.argv[sys.argv.index('--entry')+1] if '--entry' in sys.argv else os.path.join(ROOT,'metascience-loop-handoff/START-HERE.md')
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]+|[\u4e00-\u9fff]{1,4}")
def words(p):
    try: return len(WORD_RE.findall(open(p,encoding='utf-8',errors='replace').read()))
    except Exception: return 0
def classify(rel, head):
    h = head.lower()
    if any(k in h for k in ['generated', 'derived view', 'regenerate', 'do not hand-edit', 'ci-asserted']): return 'generate'
    if re.search(r'(^|/)(.*_VERBATIM\.md|EXTRACTS-.*\.md|.*\.json|(trap|ib|abc)\.txt|SEARCH-LOG.*|.*\.bundle|.*\.tar\.gz)$', rel): return 'bury'
    if re.search(r'\.tsv$|observations\.md$|A-verbatim-corrections\.md$|A-received-messages\.md$|CHANGELOG\.md$|PASS-LOG|LOG\.md$', rel): return 'accumulate'
    return 'deliver'
files = {}
for d,_,fs in os.walk(ROOT):
    if '/.git' in d or '__pycache__' in d: continue
    for f in fs:
        p=os.path.join(d,f); rel=os.path.relpath(p,ROOT)
        try: head=open(p,encoding='utf-8',errors='replace').read(600)
        except Exception: head=''
        files[rel]={'bytes':os.path.getsize(p),'class':classify(rel,head)}
# ---- fresh-ai read-in set ----
entry_txt = open(ENTRY,encoding='utf-8',errors='replace').read() if os.path.exists(ENTRY) else ''
entry_dir = os.path.dirname(ENTRY)
named = set()
for m in re.finditer(r'`([^`\n]+)`', entry_txt):
    tok=m.group(1).strip()
    for cand in (os.path.join(entry_dir,tok), os.path.join(ROOT,tok)):
        if os.path.isfile(cand): named.add(os.path.relpath(cand,ROOT)); break
for rel in files:
    if rel.startswith('metascience-loop-handoff/ledger/') or rel.startswith('metascience-loop-handoff/B-tests/'): named.add(rel)
readin = sorted(named)
ids_needed=set(); text_all=''
for rel in readin:
    try: text_all += open(os.path.join(ROOT,rel),encoding='utf-8',errors='replace').read()+'\n'
    except Exception: pass
cited = {'NEED':set(re.findall(r'NEED-(\d{4})',text_all)),'COR':set(re.findall(r'COR-(\d{4})',text_all)),'CLAIM':set(re.findall(r'CLAIM-(\d{4})',text_all)),'obs':set(re.findall(r'\bobs\.? ?(\d{2,3})\b',text_all))}
def ledger_ids(path, col=0):
    p=os.path.join(ROOT,path)
    if not os.path.exists(p): return set()
    return set(l.split('\t')[col].strip() for l in open(p,encoding='utf-8',errors='replace').read().split('\n')[1:] if l.strip())
have = {'NEED':{x.split('-')[1] for x in ledger_ids('metascience-loop-handoff/ledger/needs.tsv') if x.startswith('NEED-')},
        'COR':{x.split('-')[1] for x in ledger_ids('metascience-loop-handoff/B-tests/corrections.tsv') if x.startswith('COR-')},
        'CLAIM':{x.split('-')[1] for x in ledger_ids('metascience-loop-handoff/B-tests/claims.tsv') if x.startswith('CLAIM-')},
        'obs':set(re.findall(r'^\| (\d{1,3}) \|', open(os.path.join(ROOT,'metascience-loop-handoff/B-tests/observations.md'),encoding='utf-8').read(), re.M)) if os.path.exists(os.path.join(ROOT,'metascience-loop-handoff/B-tests/observations.md')) else set()}
dangling = {k: sorted(cited[k]-have[k]) for k in cited}
fresh = {'files':len(readin),'bytes':sum(files[r]['bytes'] for r in readin),'words':sum(words(os.path.join(ROOT,r)) for r in readin)}
fresh['ai_tokens_est']=int(fresh['words']*1.35); fresh['bury_in_readin']=[r for r in readin if files[r]['class']=='bury']
# ---- chat-user ----
pres = os.path.join(ROOT,'PRESENTED.tsv'); chat=[]
if os.path.exists(pres):
    rows=[l.split('\t') for l in open(pres,encoding='utf-8').read().split('\n')[1:] if l.strip()]
    last = rows[-1][0] if rows else None
    for r in rows:
        if r[0]!=last: continue
        p=os.path.join(ROOT,r[1]);
        if not os.path.exists(p): chat.append({'file':r[1],'missing':True}); continue
        t=open(p,encoding='utf-8',errors='replace').read()
        title=(re.search(r'^#\s+(.*)$',t,re.M) or [None,'(no H1)'])[1]
        first=re.sub(r'\s+',' ',t[:700])
        chat.append({'file':r[1],'title':title[:90],'first_screen_words':len(WORD_RE.findall(first)),
                     'verdict_in_first_screen':bool(re.search(r'你需要|需要你|verdict|判决|TL;DR|conclusion|the one action|结论|决定',first,re.I))})
# ---- maintainer ----
try:
    diff = subprocess.run(['git','-C',ROOT,'diff','--numstat','HEAD~1','HEAD','--','metascience-loop-handoff/ledger','metascience-loop-handoff/B-tests'],capture_output=True,text=True).stdout
    maint=[(l.split('\t')[2], int(l.split('\t')[0])) for l in diff.strip().split('\n') if l.strip() and l.split('\t')[0].isdigit()]
except Exception: maint=[]
classes={}
for r,v in files.items(): classes.setdefault(v['class'],[0,0]); classes[v['class']][0]+=1; classes[v['class']][1]+=v['bytes']
out={'root':ROOT,'entry':os.path.relpath(ENTRY,ROOT),'classes':{k:{'files':v[0],'bytes':v[1]} for k,v in classes.items()},
     'fresh_ai':{**fresh,'readin_files':readin,'dangling_refs':dangling},'chat_user':{'presented_last_round':chat},
     'maintainer':{'ledger_lines_added_last_commit':maint,'total_lines':sum(n for _,n in maint)}}
if '--json' in sys.argv: print(json.dumps(out,ensure_ascii=False,indent=1))
else:
    print(f"classes: " + ', '.join(f"{k}={v['files']} files/{v['bytes']:,} B" for k,v in sorted(out['classes'].items())))
    print(f"fresh-ai read-in: {fresh['files']} files, {fresh['bytes']:,} B, {fresh['words']:,} words ≈ {fresh['ai_tokens_est']:,} tokens; bury∩readin = {fresh['bury_in_readin'] or '∅'}")
    print("  dangling refs: " + ('none' if not any(dangling.values()) else json.dumps(dangling)))
    print(f"chat-user (last round presented): {len(chat)} files; " + '; '.join(f"{c['file'].split('/')[-1]} first-screen {c.get('first_screen_words')}w verdict={c.get('verdict_in_first_screen')}" for c in chat) if chat else "chat-user: no PRESENTED.tsv yet")
    print(f"maintainer: {out['maintainer']['total_lines']} ledger lines added in last commit across {len(maint)} files")
