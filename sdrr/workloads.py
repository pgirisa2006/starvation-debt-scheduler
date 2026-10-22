"""Workload generators: textbook, mixed and starvation-prone."""
import random
from typing import List

from .process import Process


def textbook() -> List[Process]:
    arrivals = [0, 1, 2, 3, 4, 5, 6]
    bursts = [24, 3, 3, 12, 5, 30, 4]
    prios = [1, 1, 2, 3, 1, 3, 2]
    return [Process(f"P{i+1}", a, b, pr)
            for i, (a, b, pr) in enumerate(zip(arrivals, bursts, prios))]


def mixed(seed: int = 0, n: int = 12) -> List[Process]:
    rng = random.Random(seed)
    procs = []
    for i in range(n):
        burst = rng.randint(2, 8) if rng.random() < 0.6 else rng.randint(20, 60)
        procs.append(Process(f"P{i+1}", rng.randint(0, 150), burst, rng.randint(1, 5)))
    return procs


def starvation(seed: int = 0, n_long: int = 3, n_short: int = 20) -> List[Process]:
    rng = random.Random(seed)
    procs = [Process(f"L{i+1}", 0, rng.randint(50, 80), rng.randint(3, 5))
             for i in range(n_long)]
    t = 0
    for i in range(n_short):
        t += rng.randint(2, 8)           # steady stream of short jobs
        procs.append(Process(f"S{i+1}", t, rng.randint(3, 6), rng.randint(1, 3)))
    return procs


GENERATORS = {
    "textbook": lambda seed=0: textbook(),
    "mixed": mixed,
    "starvation": starvation,
}
