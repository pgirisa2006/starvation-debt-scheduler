"""FCFS, SJF, Priority, Round Robin and Starvation-Debt Round Robin (SDRR).

Every scheduler takes a list of Process objects and returns
(finished_processes, timeline) where timeline is a list of
(pid, start, end) execution slices.  Inputs are never modified.
"""
import math
from collections import deque
from dataclasses import dataclass
from typing import Callable, List, Tuple

from .process import Process, clone_all

Timeline = List[Tuple[str, int, int]]


# ----------------------------------------------------------------- baselines
def _non_preemptive(processes, pick: Callable[[List[Process]], Process]):
    procs = clone_all(processes)
    pending = sorted(procs, key=lambda p: (p.arrival, p.pid))
    ready: List[Process] = []
    timeline: Timeline = []
    t, done = 0, []
    while pending or ready:
        while pending and pending[0].arrival <= t:
            ready.append(pending.pop(0))
        if not ready:
            t = pending[0].arrival
            continue
        p = pick(ready)
        ready.remove(p)
        p.start_time = t
        p.longest_gap = t - p.arrival
        t += p.burst
        p.remaining, p.service = 0, p.burst
        p.completion_time = t
        timeline.append((p.pid, p.start_time, t))
        done.append(p)
    return done, timeline


def fcfs(processes):
    return _non_preemptive(processes, lambda r: r[0])


def sjf(processes):
    return _non_preemptive(processes, lambda r: min(r, key=lambda p: p.burst))


def priority(processes):
    return _non_preemptive(processes, lambda r: min(r, key=lambda p: p.priority))


def round_robin(processes, quantum: int = 4):
    procs = clone_all(processes)
    pending = sorted(procs, key=lambda p: (p.arrival, p.pid))
    queue: deque = deque()
    ready_since = {}
    timeline: Timeline = []
    t, done = 0, []

    def admit(now):
        while pending and pending[0].arrival <= now:
            p = pending.pop(0)
            queue.append(p)
            ready_since[p.pid] = p.arrival

    admit(t)
    while pending or queue:
        if not queue:
            t = pending[0].arrival
            admit(t)
            continue
        p = queue.popleft()
        if p.start_time is None:
            p.start_time = t
        p.longest_gap = max(p.longest_gap, t - ready_since[p.pid])
        run = min(quantum, p.remaining)
        timeline.append((p.pid, t, t + run))
        t += run
        p.remaining -= run
        p.service += run
        admit(t)                      # arrivals join ahead of the pre-empted process
        if p.remaining > 0:
            p.preemptions += 1
            ready_since[p.pid] = t
            queue.append(p)
        else:
            p.completion_time = t
            done.append(p)
    return done, timeline


# ---------------------------------------------------------------------- SDRR
@dataclass
class SDRRParams:
    base_quantum: int = 4          # Q0
    alpha: float = 1.0             # debt gained per Q0 of waiting
    beta: float = 0.5              # debt added on pre-emption
    gamma: float = 0.1             # debt added per denial
    rho: float = 1.0               # debt recovery rate
    k: float = 0.5                 # quantum growth per unit of debt
    max_quantum_factor: float = 2.0
    service_scale: float = 2.0     # sigma: service damping on waiting debt

    @property
    def q_max(self) -> float:
        return self.max_quantum_factor * self.base_quantum


def sdrr(processes, params: SDRRParams = None):
    P = params or SDRRParams()
    procs = clone_all(processes)
    pending = sorted(procs, key=lambda p: (p.arrival, p.pid))
    ready: List[Process] = []          # queue order breaks debt ties
    last_update = {}                   # time up to which waiting debt is booked
    ready_since = {}
    timeline: Timeline = []
    t, done = 0, []

    def admit(now):
        while pending and pending[0].arrival <= now:
            p = pending.pop(0)
            ready.append(p)
            last_update[p.pid] = p.arrival
            ready_since[p.pid] = p.arrival

    def book_waiting(now):
        """Accrue waiting debt for every ready process, damped by service."""
        for p in ready:
            waited = now - last_update[p.pid]
            if waited > 0:
                damp = 1.0 / (1.0 + p.service / (P.service_scale * P.base_quantum))
                p.add_debt(P.alpha * waited / P.base_quantum * damp)
                last_update[p.pid] = now

    admit(t)
    while pending or ready:
        if not ready:
            t = pending[0].arrival
            admit(t)
            continue

        book_waiting(t)
        # loop 1: process selection - highest debt wins, queue order breaks ties
        p = max(ready, key=lambda x: x.debt)
        ready.remove(p)
        for other in ready:                       # everyone else was denied the CPU
            other.denials += 1
            other.add_debt(P.gamma)

        # loop 2: quantum from debt, capped at Q_max
        q = min(P.q_max, P.base_quantum + P.k * p.debt)
        q = max(1, int(math.ceil(q)))

        if p.start_time is None:
            p.start_time = t
        p.longest_gap = max(p.longest_gap, t - ready_since[p.pid])
        run = min(q, p.remaining)
        timeline.append((p.pid, t, t + run))
        t += run
        p.remaining -= run
        p.service += run

        # debt recovery for the process that just ran
        p.debt *= math.exp(-P.rho * run / P.base_quantum)

        admit(t)
        book_waiting(t)               # time spent waiting while p was running
        if p.remaining > 0:
            p.preemptions += 1
            p.add_debt(P.beta)        # pre-empted before finishing
            last_update[p.pid] = t
            ready_since[p.pid] = t
            ready.append(p)
        else:
            p.completion_time = t
            done.append(p)
    return done, timeline


ALGORITHMS = {
    "FCFS": fcfs,
    "SJF": sjf,
    "Priority": priority,
    "Round Robin": round_robin,
    "SDRR": sdrr,
}
