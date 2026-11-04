#!/usr/bin/env python3
"""theory/proto.py -- a prototype for the record theory (emu #32), run on real evidence.  Stdlib only.

Not the record format and not the worker's implementation: an instrument for the argument in theory/RECORD-THEORY.md.

What it does, on docs/evidence/hw1-correction-2026-10-03/:
  1. turns the step transcription into L1 assertions, each with a ROLE (predictor / behaviour / outcome / belief /
     state / opinion / structure / world), an asserter, an encoder, a modality and a scope;
  2. adds a second encoding pass for predictors the narration states but the transcription did not key, each with a
     verbatim quote (checked);
  3. evaluates ten verifiers in three-valued logic (FINDING / PASS / UNDECIDED) under five lenses;
  4. checks the decisions against the narrator's reported outcomes, which are HELD OUT: no verifier reads an outcome.

Run:  python3 theory/proto.py            (writes theory/RESULTS.md)
"""
from __future__ import annotations
import json, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "docs/evidence/hw1-correction-2026-10-03"
NARR = (EV / "narration.zh.txt").read_text(encoding="utf-8")
STEPS = [json.loads(l) for l in (EV / "transcription.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
BY_ID = {s["id"]: s for s in STEPS}

# ---- 1. roles of the narrator's stated keys -------------------------------------------------------------------
# predictor: a property of the artifact or situation, measurable in principle without asking the person
# behaviour: what the person did;  outcome: what happened to the person (cost felt, goal lost, confusion, doubt)
# belief: what the person took to be true;  state: memory content or goal criterion;  opinion: evaluation/suggestion
ROLE = {
    "anchor": "predictor", "confusables": "predictor", "reading": "predictor", "keyword": "predictor",
    "keywords": "predictor", "filter": "predictor", "reversibility": "predictor", "feedback": "predictor",
    "progress": "predictor",
    "enumerate": "behaviour", "narrowing": "behaviour", "candidates": "behaviour", "plan": "behaviour",
    "scroll": "behaviour", "loop": "behaviour",
    "memory": "outcome", "cost": "outcome", "inference": "outcome", "counted_as": "outcome", "review": "outcome",
    "dithering": "outcome", "doubt": "outcome",
    "belief": "belief", "verify": "belief", "reasoning": "belief",
    "key": "state", "completeness": "state",
    "proposal": "opinion",
}

def A(subject, pred, value, role, asserted_by, modality, evidence=None, encoded_by="transcriber", scope=None):
    if evidence is not None and evidence not in NARR:
        raise SystemExit(f"evidence for {subject}.{pred} is not verbatim: {evidence!r}")
    return dict(subject=subject, pred=pred, value=value, role=role, asserted_by=asserted_by, encoded_by=encoded_by,
                modality=modality, evidence=evidence, scope=scope or BY_ID.get(subject, {}).get("scope", "2026-10-03"))

L1 = []
for s in STEPS:
    sid = s["id"]
    for k in ("kind", "op", "surface"):
        if s.get(k): L1.append(A(sid, k, s[k], "structure", "transcriber", "encoded", s.get("quote")))
    if s.get("parent"): L1.append(A(sid, "part_of", s["parent"], "structure", "transcriber", "encoded", s.get("quote")))
    if s.get("t"): L1.append(A(sid, "at", s["t"], "structure", "screenshot-clock", "measured", encoded_by="transcriber"))
    for k, quotes in (s.get("stated") or {}).items():
        for q in quotes:
            L1.append(A(sid, k, q, ROLE[k], "narrator", "stated", q))
    for k, v in (s.get("inferred") or {}).items():
        L1.append(A(sid, k, v, "belief" if "belief" in k else "predictor", "transcriber", "inferred"))

# ---- 2. second encoding pass: normalised predictor values -----------------------------------------------------
# (a) normalising the stated quotes the verifiers read
NORM = {
    ("anchor", "固定位置"): "fixed-position", ("anchor", "鹤立鸡群于文字之中"): "unique-visual",
    ("anchor", "有手机屏幕物理边界作为nav anchor"): "edge", ("anchor", "有屏幕物理边界定位"): "edge",
    ("anchor", "一边做空间定位"): "none", ("anchor", "unmistakable的标题"): "unique-visual", ("anchor", "好anchor"): "unique-visual",
    ("confusables", "无混淆项"): 0, ("confusables", "一堆长得差不多的乱码"): 5,
    ("confusables", "不会和刚经手过的长得非常像的script文件搞混"): 1,
    ("feedback", "不确定刷了没"): "none", ("progress", "使劲上滑，页面反复瞬间跳回顶部"): "view-jumps",
    ("reversibility", "幂等操作，无后果"): "idempotent",
}
for a in L1:
    if a["role"] == "predictor" and (a["pred"], a["value"]) in NORM:
        a["norm"] = NORM[(a["pred"], a["value"])]
# (b) predictors the narration states but the transcription did not key: stated by the narrator, encoded now
PASS2 = [
    ("G3", "restores", "lost-position", "stated", "一刷又回到了题目页面"),
    ("E5", "feedback", "none", "stated", "完了，卡住了"),
    ("G1", "feedback", "none", "stated", "点了Apply，又卡住了"),
    ("G2", "progress", "unresponsive", "stated", "尝试滑动×n，无果"),
    ("I2", "boundary_visible", False, "stated", "为啥[key]行和comment行完全这样不需阅读内容就能identify的分界标志"),
    ("D2", "detail_available", False, "stated", "summary comment点击看不到详情"),
    ("F1", "label_says_update", False, "stated", "没有一个卡片上写着“update”的"),
    # inferred by the transcriber from what the narrator did or said (kept apart by modality)
    ("E1", "set_visibly_complete", False, "inferred", "确认“是不是所有可能选项都在这一屏里”"),
    ("G1", "colocation", False, "inferred", "summary comment点击看不到详情"),
    ("G7", "colocation", False, "inferred", "summary comment点击看不到详情"),
    ("D3", "list_origin_stated", False, "inferred", "只可能是已经知道有correction的需求了"),
    ("H4", "verify_kinds_offered", ("consistency",), "inferred", "只check一致性不check正确性"),
]
for sid, k, v, mod, q in PASS2:
    a = A(sid, k, v, "predictor", "narrator" if mod == "stated" else "transcriber", mod, q)
    a["norm"] = v; a["pass"] = 2
    L1.append(a)
# (c) facts about the artifact itself (TapGrade 0.6.5 as shipped; asserted by the artifact, encoded from its code)
L1 += [dict(subject="G0", pred="paths_for_intent", value=2, norm=2, role="predictor", asserted_by="artifact:TapGrade-0.6.5",
            encoded_by="transcriber", modality="designed", evidence=None, scope="2026-10-03",
            note="update Canvas: Re-sync view + Settings > Load a file for corrections"),
       dict(subject="H", pred="verify_kinds_offered", value=("consistency",), norm=("consistency",), role="predictor",
            asserted_by="artifact:TapGrade-0.6.5", encoded_by="transcriber", modality="designed", evidence=None,
            scope="2026-10-03", note="the scan compares with the bank; no read-back against intent")]
# (d) world state from screenshots, and the narrator's belief at the same time
L1 += [dict(subject="world", pred="corrections_loaded", value=False, at=t, role="world", asserted_by=f"screenshot:{f}",
            encoded_by="transcriber", modality="measured", scope="2026-10-03")
       for t, f in (("12:59", "IMG_0680.png"), ("13:00", "IMG_0683.png"))]
L1 += [dict(subject="world", pred="corrections_loaded", value=True, at="13:30", role="world", asserted_by="screenshot:IMG_0689.png",
            encoded_by="transcriber", modality="measured", scope="2026-10-03")]
L1 += [dict(subject="D3", pred="believes", value=("corrections_loaded", True), at="13:00", role="belief", asserted_by="narrator",
            encoded_by="transcriber", modality="stated", evidence="只可能是已经知道有correction的需求了", scope="2026-10-03")]

# ---- 3. lenses ----------------------------------------------------------------------------------------------
# A lens admits predictor assertions by (asserter kind, modality); C5's defaults fill silence only in lens "D".
def admits(lens, a):
    art = a["asserted_by"].startswith("artifact") or a["modality"] in ("measured", "designed")
    if lens == "S":   return a["asserted_by"] == "narrator" and a["modality"] == "stated"
    if lens == "A":   return art
    if lens == "SA":  return admits("S", a) or admits("A", a)
    if lens == "SAI": return admits("SA", a) or a["modality"] == "inferred"
    if lens == "D":   return admits("SAI", a)
    raise ValueError(lens)
C5_DEFAULTS = {"anchor": "none", "confusables": 0, "feedback": "immediate", "progress": "steady", "restores": "everything",
               "colocation": True, "set_visibly_complete": True, "list_origin_stated": True, "verify_kinds_offered": ("consistency", "correctness"),
               "boundary_visible": True, "detail_available": True, "label_says_update": True, "paths_for_intent": 1}
LENSES = ["S", "A", "SA", "SAI", "D"]

def pred_value(lens, subject, key):
    vals = [a.get("norm", a["value"]) for a in L1 if a["subject"] == subject and a["pred"] == key and a["role"] == "predictor"
            and admits(lens, a) and "norm" in a]
    if vals: return vals[0]
    if lens == "D" and key in C5_DEFAULTS: return C5_DEFAULTS[key]
    return None                                                     # silence: not "none", not a default

# ---- 4. verifiers, three-valued --------------------------------------------------------------------------------
F, P, U = "FINDING", "PASS", "UNDECIDED"
POSITIONAL = {"edge", "fixed-position", "unique-visual"}
def v_anchoring(L, s):
    a = pred_value(L, s, "anchor")
    if a in POSITIONAL: return P
    c = pred_value(L, s, "confusables")
    if a is not None and c is not None: return F if c > 0 else P
    return U
def v_candidate(L, s):
    v = pred_value(L, s, "set_visibly_complete"); return U if v is None else (P if v else F)
def v_interruption(L, s):
    v = pred_value(L, s, "restores"); return U if v is None else (P if v == "everything" else F)
def v_colocation(L, s):
    v = pred_value(L, s, "colocation"); return U if v is None else (P if v else F)
def v_progress(L, s):
    fb, pr = pred_value(L, s, "feedback"), pred_value(L, s, "progress")
    if fb == "none" or pr in ("view-jumps", "unresponsive"): return F
    if fb is not None and pr is not None: return P
    return U
def v_causal(L, s):
    v = pred_value(L, s, "list_origin_stated"); return U if v is None else (P if v else F)
def v_single_path(L, s):
    v = pred_value(L, "G0", "paths_for_intent"); return U if v is None else (F if v > 1 else P)
def v_correctness(L, s):
    v = pred_value(L, s, "verify_kinds_offered") or pred_value(L, "H", "verify_kinds_offered")
    return U if v is None else (P if "correctness" in v else F)
def v_separators(L, s):
    v = pred_value(L, s, "boundary_visible"); return U if v is None else (P if v else F)
def v_memory(L, s):
    # needs slot contents (need/held): nobody stated them; only C5's per-op defaults decide it
    return P if L == "D" else U
def v_labels(L, s):
    v = pred_value(L, s, "label_says_update"); return U if v is None else (P if v else F)

VERIFIERS = [  # name, trigger, function, outcome keys that would corroborate a finding (held out)
    ("anchoring",    lambda s: s.get("op") in ("SCAN", "DISCRIMINATE", "ANCHOR"), v_anchoring, {"dithering", "inference", "memory", "cost"}),
    ("memory",       lambda s: s.get("kind") == "step", v_memory, {"memory"}),
    ("candidate_set",lambda s: s.get("op") == "ENUMERATE", v_candidate, {"memory", "cost"}),
    ("interruption", lambda s: s.get("op") in ("REFRESH", "NAVIGATE"), v_interruption, {"memory"}),
    ("colocation",   lambda s: s.get("op") == "COMMIT" and s["id"] != "D1", v_colocation, {"doubt", "review"}),
    ("progress",     lambda s: s.get("op") in ("WAIT", "COMMIT"), v_progress, {"memory", "doubt"}),
    ("causal",       lambda s: s.get("op") == "INFER", v_causal, {"belief"}),
    ("single_path",  lambda s: s["id"] == "G0", v_single_path, {"dithering"}),
    ("correctness",  lambda s: s["id"] in ("H", "H4"), v_correctness, {"doubt"}),
    ("separators",   lambda s: s["id"] in ("I1", "I2"), v_separators, {"opinion"}),
    ("labels",       lambda s: s["id"] == "F1", v_labels, {"dithering"}),
]

# ---- 5. held-out outcomes, with polarity, under two attributions ----------------------------------------------
# An outcome reports EASE ("marginal cost 0") or FRICTION ("memory burnt", "forgot why I came"); a first version
# counted every outcome as friction and so marked easy steps as contradicted.
EASE = {"边际成本为0", "辨认推理成本≈0", "逐个保存的成本约为2步", "所以这个算第一步", "所以这是第二步"}
def friction(a):
    return a["role"] == "outcome" and a["value"] not in EASE
def goal_of(sid):
    s = BY_ID.get(sid, {})
    return sid if s.get("kind") == "goal" else s.get("parent")
ORDER = [s["id"] for s in STEPS]
ATTRIBUTION = "goal"           # "goal": anywhere in the step's goal; "window": the step and the next two siblings
def outcome_in_goal(sid, keys):
    if ATTRIBUTION == "goal":
        g = goal_of(sid)
        members = {x["id"] for x in STEPS if x.get("parent") == g} | {g}
    else:
        sibs = [x["id"] for x in STEPS if x.get("parent") == BY_ID[sid].get("parent")]
        i = sibs.index(sid) if sid in sibs else 0
        members = set(sibs[i:i + 3]) | {sid}
    struct = any(BY_ID[m].get("op") in ("RELOAD", "RE-ORIENT") for m in members if m in BY_ID and m != sid)
    stated = any(a["subject"] in members and (friction(a) or (a["role"] == "belief" and "belief" in keys)) for a in L1)
    return stated or struct

def evaluate():
    rows = []
    for name, trig, fn, keys in VERIFIERS:
        for scope in ("2026-10-03", "generalized"):
            trig_steps = [s["id"] for s in STEPS if trig(s) and s.get("scope", "2026-10-03") in ((scope,) if scope == "generalized" else ("2026-10-03", "general"))]
            if not trig_steps: continue
            per = {}
            for L in LENSES:
                res = [fn(L, sid) for sid in trig_steps]
                obs = [outcome_in_goal(sid, keys) for sid in trig_steps]
                agree = sum(1 for r, o in zip(res, obs) if (r == F and o) or (r == P and not o))
                disagree = sum(1 for r, o in zip(res, obs) if (r == F and not o) or (r == P and o))
                per[L] = dict(F=res.count(F), P=res.count(P), U=res.count(U), agree=agree, disagree=disagree)
            rows.append((name, scope, len(trig_steps), per))
    return rows

def divergences():
    out = []
    for b in [a for a in L1 if a["pred"] == "believes"]:
        prop, val = b["value"]
        world = [w for w in L1 if w["role"] == "world" and w["pred"] == prop and w["at"] <= b["at"]]
        if world and world[-1]["value"] != val:
            out.append((b["subject"], b["at"], prop, val, world[-1]["value"], world[-1]["asserted_by"]))
    return out

def summary(rows):
    tot = {L: collections.Counter() for L in LENSES}
    for _, scope, n, per in rows:
        if scope != "2026-10-03": continue
        for L in LENSES:
            for k in ("F", "P", "U", "agree", "disagree"): tot[L][k] += per[L][k]
    return tot

if __name__ == "__main__":
    import sys
    alt = {}
    for att in ("goal", "window"):
        ATTRIBUTION = att
        alt[att] = summary(evaluate())
    ATTRIBUTION = "goal"
    rows = evaluate()
    roles = collections.Counter((a["role"], a["scope"]) for a in L1 if a["asserted_by"] == "narrator")
    lines = ["# Results of theory/proto.py on the HW1 evidence (generated; do not edit by hand)", "",
             f"L1 assertions: {len(L1)}; narrator-asserted by role and scope: " +
             ", ".join(f"{r}/{sc}: {n}" for (r, sc), n in sorted(roles.items())), "",
             "## Verifiers under five lenses (F finding / P pass / U undecided; agree / disagree with the held-out outcomes)", "",
             "Lenses: **S** narrator-stated predictors only; **A** artifact-sourced only (designed, measured); **SA** both;"
             " **SAI** plus transcriber inferences; **D** plus C5's defaults for silence.", "",
             "| verifier | scope | triggers | " + " | ".join(LENSES) + " |", "|---|---|---|" + "---|" * len(LENSES)]
    for name, scope, n, per in rows:
        cells = [f"{p['F']}/{p['P']}/{p['U']} ({p['agree']}:{p['disagree']})" for p in (per[L] for L in LENSES)]
        lines.append(f"| {name} | {scope} | {n} | " + " | ".join(cells) + " |")
    tot = summary(rows)
    lines += ["", "**This run (2026-10-03), all verifiers:** " + "; ".join(
        f"{L}: decided {tot[L]['F'] + tot[L]['P']} of {tot[L]['F'] + tot[L]['P'] + tot[L]['U']}, agree {tot[L]['agree']}, disagree {tot[L]['disagree']}" for L in LENSES), ""]
    lines += ["## Sensitivity to how an outcome is attributed (this run, all verifiers)", "",
              "| lens | decided | agree (goal) | disagree (goal) | agree (window) | disagree (window) |", "|---|---|---|---|---|---|"]
    for L in LENSES:
        g, w = alt["goal"][L], alt["window"][L]
        lines.append(f"| {L} | {g['F'] + g['P']} of {g['F'] + g['P'] + g['U']} | {g['agree']} | {g['disagree']} | {w['agree']} | {w['disagree']} |")
    lines += ["", "## Belief against world state", ""]
    for sid, at, prop, believed, actual, src in divergences():
        lines.append(f"- {sid} at {at}: believed `{prop} = {believed}`, world `{actual}` ({src}): a wrong inference, located at its step")
    out = "\n".join(lines) + "\n"
    (Path(__file__).parent / "RESULTS.md").write_text(out, encoding="utf-8")
    print(out)
