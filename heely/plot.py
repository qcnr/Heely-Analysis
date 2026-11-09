"""Make the preliminary plot from results/queries.csv.
Reads data from csv made in graph.py and writes it as a png plot
Compares amount of nodes to time per query
Dashed median line, shaded 25th and 75th percentile
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import statistics
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

#setting colors for graph
BLUE = "#2a78d6"
INK, MUTED, GRID = "#1f1f1e", "#6b6a66", "#e2e1dd"

#groups by grid size for plotting
def load(results_dir):
    by_v = defaultdict(lambda: defaultdict(list))
    with open(os.path.join(results_dir, "queries.csv")) as f: #need in results folder which is in same folder as this code
        for row in csv.DictReader(f):
            V = int(row["V"])
            for key in ("time_s", "settled", "cost"): #seperates values
                by_v[V][key].append(float(row[key]))
    return by_v


def make_plot(results_dir, out_dir=None):
    out_dir = out_dir or results_dir
    by_v = load(results_dir)
    V = sorted(by_v)
    q = [statistics.quantiles(by_v[v]["time_s"], n=4) for v in V]
    q1, med, q3 = [x[0] for x in q], [x[1] for x in q], [x[2] for x in q]

    #plotting with matplotlib
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    fig.patch.set_facecolor("white")
    ax.fill_between(V, q1, q3, color=BLUE, alpha=0.15, linewidth=0, zorder=2)
    ax.plot(V, med, color=BLUE, marker="o", markersize=5, linewidth=1.6,
            label="Dijkstra, median (band: quartiles)", zorder=3)
    ref = [v * math.log(v) for v in V]
    scale = med[-1] / ref[-1]
    ax.plot(V, [r * scale for r in ref], linestyle="--", color=MUTED, linewidth=1.0,
            label=r"$\propto V \log V$", zorder=2)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("nodes V (log)", color=INK)
    ax.set_ylabel("time per query, seconds (log)", color=INK)
    n_total = sum(len(by_v[v]["time_s"]) for v in V)
    ax.set_title(f"Dijkstra query time vs world size ({n_total} queries)",
                 color=INK, fontsize=11, loc="left")
    ax.grid(True, which="major", color=GRID, linewidth=0.6)
    ax.grid(True, which="minor", color=GRID, linewidth=0.3, alpha=0.6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    fig.tight_layout()
    out = os.path.join(out_dir, "preliminary_plot.png")
    fig.savefig(out, dpi=200) #throws error if preliminary_plot.png already exists so don't run more than once
    plt.close(fig)

#main to run code
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default="results")
    ap.add_argument("--out", default=None, help="output dir (default: same as --results)")
    args = ap.parse_args(argv)
    make_plot(args.results, args.out)


if __name__ == "__main__":
    main()
