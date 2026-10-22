import pytest

from sdrr.metrics import (context_switches, evaluate, jain_index, response_time,
                          turnaround_time, waiting_time)
from sdrr.process import Process
from sdrr.schedulers import ALGORITHMS, SDRRParams, fcfs, priority, round_robin, sdrr, sjf
from sdrr.workloads import mixed, starvation, textbook


def simple():
    return [Process("A", 0, 5, 2), Process("B", 1, 3, 1), Process("C", 2, 8, 3)]


@pytest.mark.parametrize("name", list(ALGORITHMS))
def test_all_processes_finish_with_full_service(name):
    done, timeline = ALGORITHMS[name](textbook())
    assert len(done) == 7
    for p in done:
        assert p.remaining == 0 and p.completion_time >= p.arrival + p.burst
    assert sum(e - s for _, s, e in timeline) == sum(p.burst for p in textbook())


@pytest.mark.parametrize("name", list(ALGORITHMS))
def test_timeline_has_no_overlap(name):
    _, timeline = ALGORITHMS[name](mixed(3))
    for (_, _, e1), (_, s2, _) in zip(timeline, timeline[1:]):
        assert e1 <= s2


def test_inputs_not_modified():
    procs = simple()
    sdrr(procs)
    assert all(p.remaining == p.burst and p.start_time is None for p in procs)


def test_fcfs_order():
    done, _ = fcfs(simple())
    assert [p.pid for p in done] == ["A", "B", "C"]


def test_sjf_picks_shortest_ready():
    done, _ = sjf([Process("A", 0, 10), Process("B", 1, 8), Process("C", 1, 2)])
    assert [p.pid for p in done] == ["A", "C", "B"]


def test_priority_lower_number_first():
    done, _ = priority([Process("A", 0, 4, 5), Process("B", 1, 4, 2), Process("C", 1, 4, 1)])
    assert [p.pid for p in done] == ["A", "C", "B"]


def test_round_robin_quantum():
    _, timeline = round_robin([Process("A", 0, 10), Process("B", 0, 10)], quantum=4)
    assert all(e - s <= 4 for _, s, e in timeline)


def test_sdrr_equals_rr_when_debt_disabled():
    zero = SDRRParams(alpha=0, beta=0, gamma=0)
    procs = [Process("A", 0, 10), Process("B", 0, 10), Process("C", 0, 6)]
    assert sdrr(procs, zero)[1] == round_robin(procs, 4)[1]


def test_sdrr_quantum_never_exceeds_cap():
    P = SDRRParams()
    _, timeline = sdrr(starvation(1), P)
    assert max(e - s for _, s, e in timeline) <= P.q_max


def test_sdrr_debt_is_tracked_and_recovers():
    done, _ = sdrr(textbook())
    assert any(p.peak_debt > 0 for p in done)
    assert all(p.debt <= p.peak_debt for p in done)


def test_sdrr_idle_gap_handled():
    done, timeline = sdrr([Process("A", 0, 3), Process("B", 50, 3)])
    assert done[1].start_time == 50 and len(timeline) == 2


def test_metric_definitions():
    p = Process("A", 2, 5)
    p.start_time, p.completion_time = 6, 14
    assert turnaround_time(p) == 12 and waiting_time(p) == 7 and response_time(p) == 4


def test_jain_index_bounds():
    assert jain_index([2, 2, 2]) == pytest.approx(1.0)
    assert 1 / 3 <= jain_index([1, 1, 10]) < 1.0


def test_context_switch_count():
    assert context_switches([("A", 0, 2), ("A", 2, 4), ("B", 4, 6), ("A", 6, 8)]) == 2


def test_evaluate_utilisation_full_when_no_idle():
    done, timeline = round_robin([Process("A", 0, 6), Process("B", 0, 6)])
    assert evaluate(done, timeline).cpu_utilization == pytest.approx(100.0)
