"""Measurement harness.

For each grid side length n (so V = n^2 nodes), build `--grids` random worlds,
and on each run `--queries` random (s, t) queries with Dijkstra. Record
wall-clock time, nodes settled, and edges relaxed for every query.
Correctness is checked separately by the tests (python -m pytest -q).

Usage (defaults reproduce results/queries.csv):

    python -m heely.experiment
    python -m heely.experiment --sizes 10,20,50 --grids 2 --queries 10 --out results
"""

from __future__ import annotations

import argparse
import csv
import os
import random
import time

from .dijkstra import shortest_path
from .graph import make_grid

DEFAULT_SIZES = "10,14,20,32,50,71,100"   # V = 100 ... 10,000 (proposal range)


def run(sizes: list[int], grids: int, queries: int, out: str,
        seed: int = 0, verbose: bool = True) -> None:
    os.makedirs(out, exist_ok=True)
    q_path = os.path.join(out, "queries.csv")
    rng = random.Random(seed)

    with open(q_path, "w", newline="") as qf:
        qw = csv.writer(qf)
        qw.writerow(["n", "V", "E", "grid_seed", "query", "s", "t", "cost",
                     "path_len", "time_s", "settled", "relaxed"])

        for n in sizes:
            for gi in range(grids):
                gseed = 1000 * n + gi
                g = make_grid(n, seed=gseed)

                for qi in range(queries):
                    s = rng.randrange(g.V)
                    t = rng.randrange(g.V)
                    while t == s:
                        t = rng.randrange(g.V)

                    t0 = time.perf_counter()
                    r = shortest_path(g, s, t)
                    elapsed = time.perf_counter() - t0

                    qw.writerow([n, g.V, g.E, gseed, qi, s, t, r.cost, len(r.path),
                                 f"{elapsed:.6f}", r.settled, r.relaxed])
                if verbose:
                    print(f"n={n:4d} V={g.V:6d} grid {gi + 1}/{grids}: last query "
                          f"{elapsed * 1000:.2f} ms, {r.settled} settled, "
                          f"cost {r.cost}, path length {len(r.path)}")

    if verbose:
        print(f"ran {len(sizes) * grids * queries} queries")
        print(f"wrote {q_path}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sizes", default=DEFAULT_SIZES,
                    help="comma-separated grid side lengths n (V = n^2)")
    ap.add_argument("--grids", type=int, default=3, help="worlds per size")
    ap.add_argument("--queries", type=int, default=20, help="queries per world")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results")
    args = ap.parse_args(argv)
    sizes = [int(x) for x in args.sizes.split(",") if x.strip()]
    run(sizes, args.grids, args.queries, args.out, args.seed)


if __name__ == "__main__":
    main()
