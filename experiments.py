"""Run every scheduler over many random workloads; save CSV and charts."""
import argparse
import csv
import os
from statistics import mean

from sdrr.metrics import as_dict, evaluate
from sdrr.schedulers import ALGORITHMS
from sdrr.workloads import GENERATORS

SCENARIOS = ["mixed", "starvation"]
COLUMNS = ["avg_waiting", "max_waiting", "avg_turnaround", "avg_response",
           "fairness", "context_switches", "starvation_rate",
           "waiting_variance", "cpu_utilization"]


def run_scenario(scenario, runs):
    acc = {name: [] for name in ALGORITHMS}
    for seed in range(runs):
        procs = GENERATORS[scenario](seed)
        for name, algo in ALGORITHMS.items():
            done, timeline = algo(procs)
            acc[name].append(as_dict(evaluate(done, timeline)))
    return {name: {c: mean(r[c] for r in rows) for c in COLUMNS}
            for name, rows in acc.items()}


def save_csv(scenario, table):
    with open(f"results/summary_{scenario}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["algorithm"] + COLUMNS)
        for name, row in table.items():
            w.writerow([name] + [round(row[c], 2) for c in COLUMNS])


def save_chart(scenario, table):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    metrics = ["avg_waiting", "avg_turnaround", "avg_response", "context_switches"]
    fig, axes = plt.subplots(1, len(metrics), figsize=(16, 4))
    for ax, m in zip(axes, metrics):
        ax.bar(list(table), [table[n][m] for n in table])
        ax.set_title(m.replace("_", " "))
        ax.tick_params(axis="x", rotation=45)
    fig.suptitle(f"Scheduler comparison - {scenario} workload")
    fig.tight_layout()
    fig.savefig(f"results/comparison_{scenario}.png", dpi=120)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=200)
    args = ap.parse_args()
    os.makedirs("results", exist_ok=True)
    for scenario in SCENARIOS:
        table = run_scenario(scenario, args.runs)
        save_csv(scenario, table)
        save_chart(scenario, table)
        print(f"\n=== {scenario} ({args.runs} workloads) ===")
        print(f"{'Algorithm':<13}" + "".join(f"{c[:10]:>12}" for c in COLUMNS))
        for name, row in table.items():
            print(f"{name:<13}" + "".join(f"{row[c]:>12.2f}" for c in COLUMNS))


if __name__ == "__main__":
    main()
