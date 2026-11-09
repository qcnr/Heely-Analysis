"""Correctness tests for Dijkstra. Run with:  python -m pytest -q

1. A hand-built world with answers worked out by hand.
2. Brute force on tiny worlds: try every possible path, take the cheapest,
   and check Dijkstra gets the same cost.
3. On larger worlds, where brute force is too slow, check Dijkstra's
   distances directly: d[s] = 0, no edge can make any distance smaller
   (d[v] <= d[u] + w for every edge), and every node's distance is reached
   by a real edge from its parent. Distances that pass all three are the
   true shortest distances, so no second algorithm is needed.
4. Every returned route is a real path whose cost matches the reported cost.
"""

import random

import pytest

from heely import dijkstra, make_grid, shortest_path
from heely.graph import graph_from_elevation

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
