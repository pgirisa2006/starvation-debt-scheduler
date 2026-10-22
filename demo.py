"""Run all five schedulers on one workload, print tables, save Gantt charts."""
import argparse
import os

from sdrr.metrics import evaluate, response_time, turnaround_time, waiting_time
from sdrr.schedulers import ALGORITHMS
from sdrr.workloads import GENERATORS


def gantt(name, timeline, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    pids = sorted({pid for pid, _, _ in timeline})
    row = {pid: i for i, pid in enumerate(pids)}
    fig, ax = plt.subplots(figsize=(10, 0.5 * len(pids) + 1.5))
    for pid, s, e in timeline:
        ax.barh(row[pid], e - s, left=s, edgecolor="black")
    ax.set_yticks(range(len(pids)))
    ax.set_yticklabels(pids)
    ax.set_xlabel("Time")
    ax.set_title(f"Gantt chart - {name}")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workload", choices=GENERATORS, default="textbook")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    os.makedirs("results", exist_ok=True)
    procs = GENERATORS[args.workload](args.seed)
    summary = []
    for name, algo in ALGORITHMS.items():
        done, timeline = algo(procs)
        done.sort(key=lambda p: p.pid)
        print(f"\n=== {name} ===")
        print(f"{'PID':<5}{'Arr':>5}{'Burst':>7}{'Start':>7}{'Done':>7}"
              f"{'Wait':>7}{'TAT':>7}{'Resp':>7}{'Preempt':>9}")
        for p in done:
            print(f"{p.pid:<5}{p.arrival:>5}{p.burst:>7}{p.start_time:>7}"
                  f"{p.completion_time:>7}{waiting_time(p):>7}{turnaround_time(p):>7}"
                  f"{response_time(p):>7}{p.preemptions:>9}")
        summary.append((name, evaluate(done, timeline)))
        gantt(name, timeline, f"results/gantt_{args.workload}_{name.replace(' ', '_')}.png")

    print("\n=== Summary ===")
    print(f"{'Algorithm':<13}{'AvgWait':>9}{'MaxWait':>9}{'AvgTAT':>9}"
          f"{'AvgResp':>9}{'Fairness':>10}{'CtxSw':>7}")
    for name, r in summary:
        print(f"{name:<13}{r.avg_waiting:>9.2f}{r.max_waiting:>9.0f}{r.avg_turnaround:>9.2f}"
              f"{r.avg_response:>9.2f}{r.fairness:>10.2f}{r.context_switches:>7}")


if __name__ == "__main__":
    main()
