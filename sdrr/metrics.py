"""Performance metrics for a finished schedule."""
from dataclasses import dataclass
from typing import Dict, List

from .process import Process

STARVATION_THRESHOLD = 60


def turnaround_time(p: Process) -> int:
    return p.completion_time - p.arrival


def waiting_time(p: Process) -> int:
    return turnaround_time(p) - p.burst


def response_time(p: Process) -> int:
    return p.start_time - p.arrival


def jain_index(values: List[float]) -> float:
    s = sum(values)
    sq = sum(v * v for v in values)
    return (s * s) / (len(values) * sq) if sq else 1.0


def context_switches(timeline) -> int:
    return sum(1 for a, b in zip(timeline, timeline[1:]) if a[0] != b[0])


def starvation_rate(procs: List[Process], threshold: int = STARVATION_THRESHOLD) -> float:
    return 100.0 * sum(1 for p in procs if p.longest_gap > threshold) / len(procs)


@dataclass
class Result:
    avg_waiting: float
    max_waiting: float
    avg_turnaround: float
    avg_response: float
    fairness: float
    context_switches: int
    starvation_rate: float
    waiting_variance: float
    cpu_utilization: float


def evaluate(procs: List[Process], timeline) -> Result:
    n = len(procs)
    waits = [waiting_time(p) for p in procs]
    mean_w = sum(waits) / n
    busy = sum(e - s for _, s, e in timeline)
    makespan = max(p.completion_time for p in procs) - min(p.arrival for p in procs)
    return Result(
        avg_waiting=mean_w,
        max_waiting=max(waits),
        avg_turnaround=sum(turnaround_time(p) for p in procs) / n,
        avg_response=sum(response_time(p) for p in procs) / n,
        fairness=jain_index([turnaround_time(p) / p.burst for p in procs]),
        context_switches=context_switches(timeline),
        starvation_rate=starvation_rate(procs),
        waiting_variance=sum((w - mean_w) ** 2 for w in waits) / n,
        cpu_utilization=100.0 * busy / makespan if makespan else 100.0,
    )


def as_dict(r: Result) -> Dict[str, float]:
    return r.__dict__.copy()
