"""Process control block used by every scheduler."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Process:
    pid: str
    arrival: int
    burst: int
    priority: int = 0          # lower number = higher priority

    # runtime state
    remaining: int = field(init=False)
    start_time: Optional[int] = field(default=None, init=False)
    completion_time: Optional[int] = field(default=None, init=False)
    preemptions: int = field(default=0, init=False)
    denials: int = field(default=0, init=False)
    debt: float = field(default=0.0, init=False)
    peak_debt: float = field(default=0.0, init=False)
    longest_gap: int = field(default=0, init=False)   # longest ready-but-not-running gap
    service: int = field(default=0, init=False)       # CPU time received so far

    def __post_init__(self):
        self.remaining = self.burst

    def add_debt(self, amount: float) -> None:
        self.debt += amount
        self.peak_debt = max(self.peak_debt, self.debt)


def clone_all(processes: List[Process]) -> List[Process]:
    """Fresh copies (state reset) so one workload can feed every algorithm."""
    return [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
