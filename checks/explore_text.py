"""checks/explore_text.py -- the `explore` layer's harness mechanics, text backend, no Chromium.

Seed 3 of the bootstrap described in the MetaProof proposal (§7.2,
https://github.com/yulinl2/MetaProof/tree/proposal/repair-front-2026-09/proposal ): the
exploration semantics of docs/EXPLORE-SPEC.md are backend-independent, so they are built first
on the cheapest page there is -- a Markdown heading tree -- and the browser backend
(checks/explore_step.py + a decider) is the same loop with different render and act functions.

What this file owns: a reader with a bounded window and a bounded, decaying memory, who
navigates a tree to answer a task, with a *pluggable* policy (scripted for deterministic tests;
a model for measurement) and explicit impairment knobs (dose curve). What it does not own: the
reader's competence.

The trace carries the three fields that checks/test_explore_text.py asserts -- and that the
falsified "blind by default" smoke layer cannot produce (README, Falsified row 3):
  depth        = number of `open` actions in one chain (recursion depth)
  memory_refs  = steps whose decision referenced a note written at an earlier step
  affordance_ok= every `open` targeted something visible in the previous observation

Exploration semantics:
  observation  = {task, view, affordances, memory, step}
  view         = "toc" (headings only) or a window of `w` lines inside a node
  affordances  = headings / links / section references parsed from the current view (never hard-coded)
  memory       = the last `mem_capacity` notes the policy chose to keep (decay = drop oldest)
  actions      = open(node_id) | scroll(delta) | zoom_out() | note(text) | answer(text)
Impairment knobs: `p_drop` (each view line dropped independently), `eps_misnav` (open a random
sibling instead), `mem_capacity`. All randomness seeded.
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import Callable, Protocol

# --- minimal heading-tree parser (inlined so this file has no kit-external dependency) --------
CJK_NUM = "零一二三四五六七八九十"
_CJK_TO_INT = {c: i for i, c in enumerate(CJK_NUM)}


def cjk_to_int(s: str):
    """'七' -> 7, '十二' -> 12, '12' -> 12; None if not a numeral."""
    if s.isdigit():
        return int(s)
    if not s or any(c not in _CJK_TO_INT for c in s):
        return None
    if s == "十":
        return 10
    if "十" in s:
        a, b = s.split("十", 1)
        return (_CJK_TO_INT[a] if a else 1) * 10 + (_CJK_TO_INT[b] if b else 0)
    return _CJK_TO_INT[s]


@dataclass
class Heading:
    level: int
    title: str
    line: int
    ordinal: int | None = None
    path: str = ""


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_ORDINAL_RE = re.compile(r"^\s*(?:第\s*)?([一二三四五六七八九十]+|\d+)(?:[、.．)）\s]|\s*节)")
_FENCE_RE = re.compile(r"^\s*(```|~~~)")


def heading_tree(md: str) -> list[Heading]:
    out: list[Heading] = []
    stack: list[Heading] = []
    in_fence = False
    for i, line in enumerate(md.splitlines()):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = _HEADING_RE.match(line)
        if not m:
            continue
        level, title = len(m.group(1)), m.group(2).strip()
        om = _ORDINAL_RE.match(title)
        h = Heading(level=level, title=title, line=i, ordinal=cjk_to_int(om.group(1)) if om else None)
        while stack and stack[-1].level >= level:
            stack.pop()
        h.path = " > ".join([s.title for s in stack] + [title])
        stack.append(h)
        out.append(h)
    return out


def _ordinal(title: str):
    m = _ORDINAL_RE.match(title)
    return cjk_to_int(m.group(1)) if m else None

_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(#([^)\s]+)\)")
_SEC_REF_RE = re.compile(r"第\s*([一二三四五六七八九十]+|\d+)\s*节")


@dataclass
class Node:
    id: int
    level: int
    title: str
    path: str
    start: int   # first line (the heading line)
    end: int     # exclusive
    parent: int | None
    children: list[int] = field(default_factory=list)


class Page:
    """A Markdown artifact as a tree of nodes with line ranges."""

    def __init__(self, md: str):
        self.lines = md.splitlines()
        hs = heading_tree(md)
        self.nodes: list[Node] = [Node(0, 0, "(root)", "(root)", 0, len(self.lines), None)]
        stack: list[Node] = [self.nodes[0]]
        for h in hs:
            n = Node(len(self.nodes), h.level, h.title, h.path, h.line, len(self.lines), None)
            while stack and stack[-1].level >= h.level:
                stack.pop()
            n.parent = stack[-1].id
            stack[-1].children.append(n.id)
            self.nodes.append(n)
            stack.append(n)
        # close line ranges: a node ends where the next heading of level <= its level starts
        for i, n in enumerate(self.nodes[1:], start=1):
            for m in self.nodes[i + 1:]:
                if m.level <= n.level:
                    n.end = m.start
                    break

    def toc(self) -> list[str]:
        return [f"{'  ' * (n.level - 1)}- [{n.id}] {n.title}" for n in self.nodes[1:]]

    def window(self, node_id: int, offset: int, w: int) -> list[str]:
        n = self.nodes[node_id]
        lo = min(max(n.start + offset, n.start), n.end)
        return self.lines[lo:min(lo + w, n.end)]

    def find(self, predicate: Callable[[Node], bool]) -> Node | None:
        return next((n for n in self.nodes[1:] if predicate(n)), None)


@dataclass
class Action:
    kind: str                      # open | scroll | zoom_out | note | answer
    arg: int | str | None = None
    uses_memory_from: int | None = None   # step number of the note this action relies on


class Policy(Protocol):
    def __call__(self, obs: dict) -> Action: ...


class Explorer:
    def __init__(self, page: Page, w: int = 40, mem_capacity: int = 5,
                 p_drop: float = 0.0, eps_misnav: float = 0.0, seed: int = 0):
        self.page = page
        self.w = w
        self.mem_capacity = mem_capacity
        self.p_drop = p_drop
        self.eps_misnav = eps_misnav
        self.rng = random.Random(seed)
        self.node = 0
        self.offset = 0
        self.view_mode = "toc"
        self.memory: list[tuple[int, str]] = []   # (step, note)
        self.trace: list[dict] = []

    # ---- rendering --------------------------------------------------------
    def _view_lines(self) -> list[str]:
        if self.view_mode == "toc":
            lines = self.page.toc()
        else:
            lines = self.page.window(self.node, self.offset, self.w)
        if self.p_drop > 0:
            lines = [l for l in lines if self.rng.random() >= self.p_drop]
        return lines

    def _affordances(self, lines: list[str]) -> list[dict]:
        """Headings / links / section references visible in the current view."""
        aff: list[dict] = []
        seen = set()
        for l in lines:
            m = re.match(r"\s*-\s*\[(\d+)\]\s+(.*)", l)          # toc entries
            if m:
                nid = int(m.group(1))
                if nid not in seen:
                    aff.append({"node": nid, "title": m.group(2)}); seen.add(nid)
                continue
            hm = re.match(r"^(#{1,6})\s+(.*?)\s*$", l)              # headings inside a window
            if hm:
                n = self.page.find(lambda x, t=hm.group(2).strip(): x.title == t)
                if n and n.id not in seen:
                    aff.append({"node": n.id, "title": n.title}); seen.add(n.id)
            for lm in _MD_LINK_RE.finditer(l):                       # [text](#anchor)
                n = self.page.find(lambda x, a=lm.group(2).lower(): re.sub(r"[^\w\u4e00-\u9fff-]", "", x.title.lower().replace(" ", "-")) == a)
                if n and n.id not in seen:
                    aff.append({"node": n.id, "title": n.title, "via": "link"}); seen.add(n.id)
            for sm in _SEC_REF_RE.finditer(l):                       # 第五节
                k = cjk_to_int(sm.group(1))
                n = self.page.find(lambda x, k=k: x.level == 2 and _ordinal(x.title) == k)
                if n and n.id not in seen:
                    aff.append({"node": n.id, "title": n.title, "via": "section-ref"}); seen.add(n.id)
        return aff

    def observe(self, task: str, step: int) -> dict:
        lines = self._view_lines()
        return {"task": task, "step": step, "view_mode": self.view_mode, "node": self.node,
                "offset": self.offset, "view": lines, "affordances": self._affordances(lines),
                "memory": list(self.memory)}

    # ---- acting -----------------------------------------------------------
    def act(self, a: Action, step: int) -> None:
        if a.kind == "open":
            target = int(a.arg)
            if self.eps_misnav > 0 and self.rng.random() < self.eps_misnav:
                parent = self.page.nodes[target].parent
                sibs = [c for c in self.page.nodes[parent].children if c != target] if parent is not None else []
                if sibs:
                    target = self.rng.choice(sibs)
            self.node, self.offset, self.view_mode = target, 0, "window"
        elif a.kind == "scroll":
            self.offset = max(0, self.offset + int(a.arg))
        elif a.kind == "zoom_out":
            self.view_mode = "toc"
        elif a.kind == "note":
            self.memory.append((step, str(a.arg)))
            while len(self.memory) > self.mem_capacity:
                self.memory.pop(0)               # decay: oldest first
        elif a.kind == "answer":
            pass
        else:
            raise ValueError(f"unknown action {a.kind}")

    def run(self, task: str, policy: Policy, max_steps: int = 20, expected: str | None = None) -> dict:
        answer = None
        depth = 0
        memory_refs: list[int] = []
        affordance_ok = True
        prev_aff: set[int] = set()
        for step in range(1, max_steps + 1):
            obs = self.observe(task, step)
            a = policy(obs)
            if a.kind == "open":
                depth += 1
                if int(a.arg) not in {x["node"] for x in obs["affordances"]}:
                    affordance_ok = False
            if a.uses_memory_from is not None:
                if any(s == a.uses_memory_from for s, _ in self.memory):
                    memory_refs.append(step)
                else:
                    memory_refs.append(-step)    # referenced a note that had already decayed
            self.trace.append({"step": step, "view_mode": obs["view_mode"], "node": obs["node"],
                               "n_affordances": len(obs["affordances"]), "action": a.kind, "arg": a.arg})
            self.act(a, step)
            prev_aff = {x["node"] for x in obs["affordances"]}
            if a.kind == "answer":
                answer = str(a.arg)
                break
        correct = (expected is not None and answer is not None and expected.strip() in answer)
        return {"answer": answer, "expected": expected, "correct": correct, "steps": len(self.trace),
                "depth": depth, "memory_refs": memory_refs, "affordance_ok": affordance_ok,
                "found": answer is not None, "trace": self.trace}


class ScriptedPolicy:
    """A deterministic stand-in for a model: a list of callables obs -> Action.

    Each callable may inspect `obs["affordances"]`, `obs["view"]`, and `obs["memory"]`; that is
    the point — a scripted policy that *needs* affordances and memory fails when the harness
    does not provide them, which is what the seed-2 must-fire test checks.
    """

    def __init__(self, steps: list[Callable[[dict], Action]]):
        self.steps = steps
        self.i = 0

    def __call__(self, obs: dict) -> Action:
        if self.i >= len(self.steps):
            return Action("answer", "(script exhausted)")
        f = self.steps[self.i]
        self.i += 1
        return f(obs)


def open_where(pred: Callable[[str], bool]) -> Callable[[dict], Action]:
    """Open the first affordance whose title satisfies `pred`; raise if none is visible."""
    def f(obs: dict) -> Action:
        for a in obs["affordances"]:
            if pred(a["title"]):
                return Action("open", a["node"])
        raise LookupError(f"no visible affordance satisfies the predicate at step {obs['step']}")
    return f


def note_matching(pattern: str) -> Callable[[dict], Action]:
    """Write the first regex match in the current view into memory; raise if not visible."""
    rx = re.compile(pattern)
    def f(obs: dict) -> Action:
        for l in obs["view"]:
            m = rx.search(l)
            if m:
                return Action("note", m.group(1) if m.groups() else m.group(0))
        raise LookupError(f"pattern {pattern!r} not visible at step {obs['step']}")
    return f


def answer_from_memory(step_written: int, template: str = "{note}") -> Callable[[dict], Action]:
    """Answer using the note written at `step_written`; raise if it has decayed."""
    def f(obs: dict) -> Action:
        for s, note in obs["memory"]:
            if s == step_written:
                return Action("answer", template.format(note=note), uses_memory_from=step_written)
        raise LookupError(f"note from step {step_written} is not in memory at step {obs['step']}")
    return f


def zoom_out() -> Callable[[dict], Action]:
    return lambda obs: Action("zoom_out")
