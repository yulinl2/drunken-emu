"""Tests for loop/tick.py: the scheduler's structures, ported from the source's tests, and the tick's own rules.

Time comes from LOOP_NOW and nothing sleeps. Each project is a temporary directory named in LOOP_PROJECT; HOME is temporary too.
"""
import json
import pathlib
import random
import sys

KIT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
from loop import tick  # noqa: E402
from loop.tick import ClauseList, DList, MLFQ  # noqa: E402


# the structures, ported from the source's tests: the same operations and the same expectations

def test_dlist_random_ops_keep_both_directions_consistent():
    r = random.Random(1); l = DList(); ns = []
    for i in range(400):
        op = r.choice('pbmrx')
        if op == 'p': ns.append(l.push_front(i))
        elif op == 'b': ns.append(l.push_back(i))
        elif op == 'm' and ns: n = r.choice(ns); ns[ns.index(n)] = l.move_to_front(n)
        elif op == 'r' and ns: n = ns.pop(r.randrange(len(ns))); l.remove(n)
        elif op == 'x' and ns: ns.append(l.insert_after(r.choice(ns), i))
        assert l.check()
    assert l.n == len(ns)


def test_mlfq_matches_the_naive_scan_and_the_policy():
    r = random.Random(7); q = MLFQ(base=4, levels=4, boost=10**9); ids = list(range(30)); now = 0   # boost off: this pins the hottest-first policy
    for i in ids: q.add(i, now)
    for step in range(600):
        now += r.choice([0, 1, 2, 3])
        naive = next((i for lv in q.L for i in lv if q.at[i]['due'] <= now), None)     # the same policy by brute force
        got = q.next_due(now)
        assert got == naive
        if got is not None:
            if r.random() < .25: q.missed(got, now); assert (q.at[got]['lv'], q.at[got]['due']) == (0, now)
            else: q.kept(got, now)
        for l in q.L: assert l.check()


def test_two_kept_checks_drop_a_level_and_a_miss_returns_to_the_front():
    q = MLFQ(base=4, levels=3); q.add('a', 0); q.kept('a', 0); assert q.at['a']['lv'] == 0
    q.kept('a', 4); assert (q.at['a']['lv'], q.at['a']['due']) == (1, 12)
    q.add('b', 0); q.missed('a', 20); assert q.L[0].front().val == 'a'; assert q.at['a']['lv'] == 0


def test_a_busy_hot_level_cannot_starve_an_overdue_cold_entry():
    # a check missed every few ticks sits at the front of level 0, due now; two entries sit in level 1, due at minutes 8 and 10
    q = MLFQ(base=4, levels=3); q._put('cold', 1, 0, due=8); q._put('warm', 1, 0, due=10); q.add('busy', 0)
    ran = []
    for now in range(10, 60, 2):
        got = q.next_due(now); ran.append(got)
        if got == 'busy': q.missed('busy', now)                       # missed every time
        else: q.kept(got, now)
    assert 'cold' in ran and 'warm' in ran
    assert ran.index('cold') == 6                                      # at minute 22 'cold' is 14 late, past the limit of 12: it runs
    # without the boost the same schedule never runs it
    q2 = MLFQ(base=4, levels=3, boost=10**9); q2._put('cold', 1, 0, due=8); q2.add('busy', 0); seen = []
    for now in range(10, 60, 2):
        got = q2.next_due(now); seen.append(got)
        if got == 'busy': q2.missed('busy', now)
        else: q2.kept(got, now)
    assert 'cold' not in seen


def test_clause_split_and_merge_roundtrip_keeps_order():
    c = ClauseList(); a = c.push_back('one two'); c.push_back('three'); c.split(a, 3); assert list(c) == ['one', ' two', 'three']
    c.merge(a); assert list(c) == ['one two', 'three']; assert c.check()


# the tick: one run per call, the policy's consequences, and liveness

def _project(tmp_path, monkeypatch, checks=None):
    root = tmp_path / "project"
    root.mkdir()
    if checks is not None:
        (root / "loop.json").write_text(json.dumps({"checks": checks}), encoding="utf-8")
    monkeypatch.setenv("LOOP_PROJECT", str(root))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    return root


def _call(monkeypatch, capsys, now, cmd="run"):
    monkeypatch.setenv("LOOP_NOW", str(now))
    rc = tick.main([cmd])
    return rc, json.loads(capsys.readouterr().out.strip().splitlines()[-1])


def test_a_failing_check_runs_again_at_the_next_tick(tmp_path, monkeypatch, capsys):
    _project(tmp_path, monkeypatch, [{"name": "bad", "run": ["false"], "every_s": 60}])
    rc1, first = _call(monkeypatch, capsys, 1000)
    rc2, second = _call(monkeypatch, capsys, 1001)
    assert rc1 == rc2 == 0
    assert (first["ran"], first["ok"]) == ("bad", False) and first["detail"].startswith("exit 1")
    assert (second["ran"], second["ok"]) == ("bad", False)


def test_a_kept_check_slows_down(tmp_path, monkeypatch, capsys):
    _project(tmp_path, monkeypatch, [{"name": "good", "run": ["true"], "every_s": 60}])
    _, t1000 = _call(monkeypatch, capsys, 1000)
    _, t1060 = _call(monkeypatch, capsys, 1060)
    _, t1100 = _call(monkeypatch, capsys, 1100)
    _, t1180 = _call(monkeypatch, capsys, 1180)
    assert (t1000["ran"], t1000["ok"], t1000["wait_s"]) == ("good", True, 60)     # kept once: due again one interval on
    assert (t1060["ran"], t1060["wait_s"]) == ("good", 120)                          # kept twice: one level down, interval doubled
    assert (t1100["ran"], t1100["ok"]) == (None, True)                              # nothing is due before 1180
    assert t1180["ran"] == "good"


def test_a_cold_check_overdue_by_more_than_three_intervals_runs_before_a_hot_one(tmp_path, monkeypatch, capsys):
    _project(tmp_path, monkeypatch, [{"name": "hot", "run": ["false"], "every_s": 1},
                                     {"name": "cold", "run": ["true"], "every_s": 10}])
    ran = []
    for now in range(1000, 1040):
        _, out = _call(monkeypatch, capsys, now)
        ran.append((now, out["ran"]))
        if out["ran"] == "cold":
            break
    # the hot check fails and is due at every tick; the cold one, due since 1000, is 31 s late at 1031, past three intervals of 10 s
    assert ran[-1] == (1031, "cold")
    assert all(name == "hot" for _, name in ran[:-1])


def test_liveness_names_a_check_that_never_ran_and_passes_on_a_healthy_log(tmp_path, monkeypatch, capsys):
    _project(tmp_path, monkeypatch, [{"name": "a", "run": ["true"], "every_s": 60},
                                     {"name": "b", "run": ["true"], "every_s": 60}])
    _call(monkeypatch, capsys, 1000)                                                 # runs a
    rc, out = _call(monkeypatch, capsys, 1001, "liveness")
    assert (rc, out) == (1, {"ok": False, "starved": ["b"]})
    _call(monkeypatch, capsys, 1001)                                                 # runs b
    rc, out = _call(monkeypatch, capsys, 1002, "liveness")
    assert (rc, out) == (0, {"ok": True, "starved": []})
    rc, out = _call(monkeypatch, capsys, 1181, "liveness")                           # a ran 181 s ago, past 3 x 60; b 180 s ago
    assert (rc, out) == (1, {"ok": False, "starved": ["a"]})


def test_no_checks_configured_fails_closed(tmp_path, monkeypatch, capsys):
    _project(tmp_path, monkeypatch)                                                  # no loop.json at all
    rc, out = _call(monkeypatch, capsys, 1000)
    assert (rc, out) == (1, {"ran": None, "ok": False, "detail": "no checks in loop.json"})
    rc, out = _call(monkeypatch, capsys, 1000, "liveness")
    assert rc == 1 and out["ok"] is False and out["starved"] == []
