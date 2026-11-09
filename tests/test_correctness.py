"""Tests for the checkpoint code. Run from the repo folder with:  python -m pytest -q

Dijkstra correctness:
1. A hand-built world with answers worked out by hand.
2. Brute force on tiny worlds: try every possible path, take the cheapest,
   and check Dijkstra gets the same cost.
3. On larger worlds, where brute force is too slow, check Dijkstra's
   distances directly: d[s] = 0, no edge gives a shortcut
   (d[v] <= d[u] + w for every edge), and every node's distance is reached
   by a real edge from its parent. Distances that pass these checks are the
   true shortest distances.
4. Every returned route is a real path whose cost matches the reported cost.

The other files:
5. graph.py builds the grid correctly and the same seed gives the same grid.
6. experiment.py writes a results CSV.
7. plot.py turns that CSV into a PNG.
"""

import csv
import os
import random
import sys

import pytest

# The files in heely/ import each other with plain imports
# (e.g. "from graph import Graph"), so put that folder on the path.
HEELY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "heely")
sys.path.insert(0, os.path.abspath(HEELY_DIR))

import experiment  # noqa: E402
import plot  # noqa: E402
from dijkstra import dijkstra, reconstruct, shortest_path  # noqa: E402
from graph import graph_from_elevation, make_grid  # noqa: E402

INF = float("inf")


def brute_force_cost(g, s, t):
    """Cheapest cost over every simple path from s to t (tiny worlds only)."""
    best = INF
    visited = [False] * g.V

    def dfs(u, cost_so_far):
        nonlocal best
        if cost_so_far >= best:
            return
        if u == t:
            best = cost_so_far
            return
        visited[u] = True
        for v, w in g.adj[u]:
            if not visited[v]:
                dfs(v, cost_so_far + w)
        visited[u] = False

    dfs(s, 0)
    return best


# ---------------------------------------------------------------------------
# dijkstra.py
# ---------------------------------------------------------------------------

def test_known_answer_3x3():
    # Elevations (row-major). The middle row is a ridge; corners are low.
    #   1  2  1
    #   3  4  3
    #   1  2  1
    elev = [1, 2, 1,
            3, 4, 3,
            1, 2, 1]
    g = graph_from_elevation(3, elev)
    # Top-left (0) to top-right (2): 0 -> 1 is uphill (push), 1 -> 2 is downhill (free).
    assert shortest_path(g, 0, 2).cost == 1
    # Peak (4) to any corner: everything is downhill, 0 pushes.
    for corner in (0, 2, 6, 8):
        assert shortest_path(g, 4, corner).cost == 0
    # Corner (0) to the peak (4): every route climbs twice.
    assert shortest_path(g, 0, 4).cost == 2
    # Staying put costs nothing.
    assert shortest_path(g, 5, 5).cost == 0 and shortest_path(g, 5, 5).path == [5]


@pytest.mark.parametrize("n,seed", [(2, 0), (3, 1), (3, 2), (4, 3), (4, 4)])
def test_dijkstra_matches_brute_force_all_pairs(n, seed):
    g = make_grid(n, seed)
    for s in range(g.V):
        for t in range(g.V):
            assert shortest_path(g, s, t).cost == brute_force_cost(g, s, t)


@pytest.mark.parametrize("n,seed", [(10, 0), (30, 1), (60, 2)])
def test_dijkstra_distances_are_optimal(n, seed):
    g = make_grid(n, seed)
    rng = random.Random(seed)
    for _ in range(3):
        s = rng.randrange(g.V)
        dist, parent, _, _ = dijkstra(g.adj, s)
        assert dist[s] == 0
        for u in range(g.V):
            for v, w in g.adj[u]:
                assert dist[v] <= dist[u] + w          # no edge gives a shortcut
            if u != s:
                p = parent[u]
                assert dist[u] == dist[p] + g.cost(p, u)   # reached by a real edge


def test_path_is_valid_and_cost_matches():
    g = make_grid(8, seed=3)
    rng = random.Random(1)
    for _ in range(40):
        s, t = rng.randrange(g.V), rng.randrange(g.V)
        res = shortest_path(g, s, t)
        assert res.path[0] == s and res.path[-1] == t
        assert g.path_cost(res.path) == res.cost      # raises if a hop is not an edge
        assert len(set(res.path)) == len(res.path)   # no node repeats
    # reconstruct gives an empty path when the goal was never reached
    assert reconstruct([-1, -1, -1], 0, 2) == []


# ---------------------------------------------------------------------------
# graph.py
# ---------------------------------------------------------------------------

def test_grid_is_built_correctly():
    n = 8
    g = make_grid(n, seed=3)
    assert g.V == n * n
    assert g.E == 4 * n * (n - 1)              # 4 neighbours, fewer on the edges
    for u in range(g.V):
        for v, w in g.adj[u]:
            assert w == (0 if g.elev[v] < g.elev[u] else 1)   # downhill = 0, else 1
            assert any(x == u for x, _ in g.adj[v])            # every edge goes both ways
    # Same seed gives the same grid; a different seed gives a different one.
    assert make_grid(n, seed=3).elev == g.elev
    assert make_grid(n, seed=4).elev != g.elev


# ---------------------------------------------------------------------------
# experiment.py and plot.py
# ---------------------------------------------------------------------------

def test_experiment_writes_csv(tmp_path):
    experiment.run([5, 8], grids=1, queries=3, out=str(tmp_path), verbose=False)
    with open(tmp_path / "queries.csv") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2 * 1 * 3
    assert {int(r["V"]) for r in rows} == {25, 64}
    for r in rows:
        assert float(r["time_s"]) >= 0 and int(r["settled"]) >= 1


def test_plot_writes_png(tmp_path):
    experiment.run([5, 8, 10], grids=1, queries=3, out=str(tmp_path), verbose=False)
    plot.make_plot(str(tmp_path))
    out = tmp_path / "preliminary_plot.png"
    assert out.exists() and out.stat().st_size > 0
    plot.make_plot(str(tmp_path))              # running it a second time also works


# Lets you run this file directly (e.g. the Run button in VS Code) and see
# each test's result, instead of having to type "python -m pytest".
if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
