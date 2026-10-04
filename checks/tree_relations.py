#!/usr/bin/env python3
"""tree_relations — the relations a directory tree implies but does not state.

  workflow instances  directories holding >=2 of the loop's ledger-file names
                      (OPEN-PROBLEMS, LATEST-CONCLUSIONS, SANDBOX-FACTS, DIR_TREE/TREE,
                      needs.tsv, firing-log.tsv, corrections.tsv, claims.tsv, observations.md,
                      CHANGELOG) -> the pipeline's shared shape, and which parts each copy lacks
  same-name pairs     the same file name in two directories: identical (one object, two sites —
                      must be edited together) or DIVERGED (the duplication failure, live)
  md5 groups          byte-identical files under different names
  derived files       headers that declare a generator ('Generated … by X') -> edge derived<-generator
  declared consumers  RELATIONS.tsv rows (src, edge, dst, evidence) maintained by hand
  storage class       every file partitioned into the three ways this loop keeps material:
                      ACCUMULATE (append-only: the verbatim record, the ledgers, the observation
                      table — never rewritten, because what was claimed is the evidence),
                      BURY (held-out/ and background/sources/: present, deliberately out of the
                      read path, opened on demand — the calibration fixture, the sealed
                      discriminators, the superseded editions, the recovered originals),
                      REGENERATE (a header declaring a generator: rebuilt from implied relations
                      at every close, so a stale copy is impossible rather than merely unlikely),
                      and UNCLASSIFIED — the bucket that is the finding, since a file in none of
                      the three has no stated rule for how it survives a round
  project mirrors     the same file name inside the read-only project-knowledge mount (--project,
                      default /mnt/project) compared by md5 against every copy under ROOT. This
                      mount is the one place divergence has ever been found here and no derived
                      view covered it until 2026-09-10-G: an instance cannot write it, so a stale
                      copy there is invisible to the append-only and manifest invariants and has
                      to be rediscovered by reading. STALE is not a failure — only the principal
                      can re-upload — but it must be visible without anyone looking for it.
Writes RELATIONS.md next to RELATIONS.tsv. Usage: python3 tree_relations.py [--root R]
"""
import os, re, sys, hashlib, collections, datetime
ROOT = sys.argv[sys.argv.index('--root')+1] if '--root' in sys.argv else os.environ.get("EMU_ROOT", os.getcwd())
LEDGER_NAMES = ['OPEN-PROBLEMS','LATEST-CONCLUSIONS','SANDBOX-FACTS','DIR_TREE|TREE','needs.tsv','firing-log.tsv','corrections.tsv','claims.tsv','observations','CHANGELOG']
files=[]
for d,_,fs in os.walk(ROOT):
    if '/.git' in d or '__pycache__' in d or '/vendor' in d: continue
    for f in fs:
        p=os.path.join(d,f)
        if os.path.getsize(p) > 20_000_000: continue
        files.append(os.path.relpath(p,ROOT))
md5={r:hashlib.md5(open(os.path.join(ROOT,r),'rb').read()).hexdigest() for r in files}
# workflow instances (group by directory; also treat metascience-loop-handoff as one instance across ledger/ and B-tests/)
def inst_key(rel):
    parts=rel.split('/')
    if parts[0]=='metascience-loop-handoff': return 'metascience-loop-handoff'
    if parts[0]=='cooperative-substrate-runner': return 'cooperative-substrate-runner'
    return os.path.dirname(rel) or '.'
inst=collections.defaultdict(set)
for r in files:
    base=os.path.basename(r)
    for n in LEDGER_NAMES:
        if re.match('^(' + n + ')', base): inst[inst_key(r)].add(n)
instances={k:v for k,v in inst.items() if len(v)>=2}
# same-name pairs
byname=collections.defaultdict(list)
for r in files: byname[os.path.basename(r)].append(r)
pairs=[]
def is_mirror(rs):
    # a mirror pair = one copy at the outputs root (or /mnt/project) and one under a package's background/ ;
    # these are ONE object at two sites and must stay byte-identical (the duplication rule)
    dirs={os.path.dirname(x) for x in rs}
    return any(d=='' for d in dirs) and any(d.endswith('background') for d in dirs)
for n,rs in byname.items():
    if len(rs)>1:
        same = len({md5[x] for x in rs})==1
        kind = 'mirror' if is_mirror(rs) else 'homonym'
        state = ('identical' if same else 'DIVERGED') if kind=='mirror' else ('identical (unexpected)' if same else 'distinct objects')
        pairs.append((n, rs, kind, state))
# md5 groups
groups=collections.defaultdict(list)
for r,h in md5.items(): groups[h].append(r)
dupes=[rs for rs in groups.values() if len(rs)>1 and len({os.path.basename(x) for x in rs})>1]
# derived files
derived=[]
for r in files:
    if not r.endswith('.md'): continue
    head=open(os.path.join(ROOT,r),encoding='utf-8',errors='replace').read(500)
    m=re.search(r'[Gg]enerated[^\n]{0,80}?by `([^`]+)`', head)
    if m: derived.append((r, m.group(1)))
# project-knowledge mount: same name, compared by md5 (read-only; an instance cannot fix a difference here)
PROJ = sys.argv[sys.argv.index('--project')+1] if '--project' in sys.argv else '/mnt/project'
proj_rows=[]
if os.path.isdir(PROJ):
    by_name=collections.defaultdict(list)
    for r in files: by_name[os.path.basename(r)].append(r)
    for f in sorted(os.listdir(PROJ)):
        pp=os.path.join(PROJ,f)
        if not os.path.isfile(pp): continue
        ph=hashlib.md5(open(pp,'rb').read()).hexdigest()
        here=by_name.get(f,[])
        if not here:
            proj_rows.append((f, ph[:8], 'PROJECT-ONLY', 'no file of this name under the outputs root', os.path.getsize(pp)))
            continue
        same=[r for r in here if md5[r]==ph]
        if same:
            proj_rows.append((f, ph[:8], 'identical', f"{len(same)} of {len(here)} copies here match", os.path.getsize(pp)))
        else:
            sizes=sorted({os.path.getsize(os.path.join(ROOT,r)) for r in here})
            proj_rows.append((f, ph[:8], 'STALE', f"outputs copies hash {md5[here[0]][:8]} at {sizes[0]:,} B; the mount has {os.path.getsize(pp):,} B", os.path.getsize(pp)))

# storage class per file: accumulate / bury / regenerate / unclassified
APPEND_ONLY_REL = set()
try:
    sz = open(os.path.join(ROOT,'metascience-loop-handoff/tools/step_zero.py'),encoding='utf-8').read()
    m = re.search(r'APPEND_ONLY\s*=\s*\[(.*?)\]', sz, re.S)
    if m: APPEND_ONLY_REL = {x.strip().strip('",\'') for x in re.findall(r'"([^"]+)"', m.group(1))}
except Exception: pass
APPEND_ONLY_REL |= {'metascience-loop-handoff/ledger/loads.tsv','PRESENTED.tsv'}
BURY_PREFIX = ('metascience-loop-handoff/held-out/','metascience-loop-handoff/background/sources/')
derived_set = {r for r,_ in derived}
cls = {}
for r in files:
    if r in APPEND_ONLY_REL: cls[r]='ACCUMULATE'
    elif r.startswith(BURY_PREFIX): cls[r]='BURY'
    elif r in derived_set: cls[r]='REGENERATE'
    else: cls[r]='UNCLASSIFIED'
cls_count = collections.Counter(cls.values())
uncl_by_dir = collections.Counter(os.path.dirname(r) or '.' for r,k in cls.items() if k=='UNCLASSIFIED')

# declared consumers
rel_tsv=os.path.join(ROOT,'RELATIONS.tsv'); declared=[]
if os.path.exists(rel_tsv):
    declared=[l.split('\t') for l in open(rel_tsv,encoding='utf-8').read().split('\n')[1:] if l.strip()]
o=[f"# RELATIONS — what the tree implies (generated {datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d %H:%M UTC} by `tools/emu_md/tree_relations.py`; regenerate, do not hand-edit)",""]
o+=["## Workflow instances — the pipeline's shared shape","","| instance | has | lacks |","|---|---|---|"]
for k,v in sorted(instances.items()):
    o.append(f"| `{k}` | {', '.join(sorted(v))} | {', '.join(sorted(set(LEDGER_NAMES)-v)) or '—'} |")
o+=["","## Same file name in two places","","*mirror = one object at two sites (root and a package's background/), must stay identical; homonym = different objects that happen to share a name.*","","| name | kind | sites | state |","|---|---|---|---|"]
for n,rs,kind,st in sorted(pairs, key=lambda x:(x[2]!='mirror', 'DIVERGED' not in x[3], x[0])):
    o.append(f"| `{n}` | {kind} | {' ; '.join('`'+x+'`' for x in rs)} | **{st}** |")
o+=["","## Storage class: how each file is meant to survive a round","",
    "*Three ways this loop keeps material, and a fourth bucket that is the finding. ACCUMULATE = append-only, never rewritten, because what was claimed is itself the evidence. "
    "BURY = present but deliberately outside the read path, opened on demand (the calibration fixture, the sealed discriminators, the superseded editions, the recovered originals). "
    "REGENERATE = declares a generator in its own header and is rebuilt from implied relations at every close, so staleness is impossible rather than merely unlikely. "
    "UNCLASSIFIED = a file with no stated rule for how it survives a round.*","",
    "| class | files | share |","|---|---|---|"]
o+= [f"| **{k}** | {cls_count[k]} | {100*cls_count[k]/max(1,len(files)):.0f}% |" for k in ('ACCUMULATE','BURY','REGENERATE','UNCLASSIFIED')]
o+=["","**Where the unclassified files are** (largest first) — each is a directory whose contents have no declared survival rule:","",
    "| directory | unclassified files |","|---|---|"]
o+= [f"| `{d}` | {c} |" for d,c in uncl_by_dir.most_common(10)]
o+=["","## Copies in the read-only project-knowledge mount",""]
o+=[f"*Compared by checksum against every copy under the outputs root. The mount at `{PROJ}` cannot be written by an instance, so a STALE row is a re-upload for the principal, not a task — the point of the row is that nobody has to go looking for it.*",""]
o+=["| file in the mount | md5 | state | detail |","|---|---|---|---|"]
o+= [f"| `{f}` | `{h}` | **{st}** | {d} |" for f,h,st,d,_ in sorted(proj_rows, key=lambda x:(x[2]!='STALE', x[2]!='PROJECT-ONLY', x[0]))] or ["| — | — | — | — |"]
o+=["","## Byte-identical files under different names","",]
o+= [f"- {' = '.join('`'+x+'`' for x in rs)}" for rs in dupes] or ["- none"]
o+=["","## Derived files and their generators","",]
o+= [f"- `{r}` ← `{g}`" for r,g in sorted(derived)] or ["- none declared"]
o+=["","## Declared consumers (from `RELATIONS.tsv`, hand-maintained)","","| src | edge | dst | evidence |","|---|---|---|---|"]
o+= [f"| {' | '.join(x[:4])} |" for x in declared] or ["| — | — | — | — |"]
open(os.path.join(ROOT,'RELATIONS.md'),'w',encoding='utf-8').write('\n'.join(o)+'\n')
mir=[p for p in pairs if p[2]=='mirror']
print(f"storage class: " + ", ".join(f"{k}={cls_count[k]}" for k in ('ACCUMULATE','BURY','REGENERATE','UNCLASSIFIED')))
print(f"project-mount: {sum(1 for r in proj_rows if r[2]=='STALE')} STALE, {sum(1 for r in proj_rows if r[2]=='PROJECT-ONLY')} project-only, {sum(1 for r in proj_rows if r[2]=='identical')} identical")
for f,h,st,d,_ in proj_rows:
    if st!='identical': print(f"  project {st:<13} {f} — {d}")
print(f"instances={len(instances)} mirror pairs={len(mir)} (DIVERGED={sum(1 for p in mir if p[3]=='DIVERGED')}) homonyms={len(pairs)-len(mir)} md5-dupes={len(dupes)} derived={len(derived)} declared={len(declared)} -> RELATIONS.md")
for n,rs,kind,st in mir: print(f"  mirror {st:<10} {n}")
