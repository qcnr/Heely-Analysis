"""Grid-world generation for the Heelys routing problem.

A world is an n x n grid of nodes. Every node has an elevation. Each node is
joined to its four grid neighbours by two directed edges (one each way), and
the cost of an edge depends on which way you are travelling along it:

    cost(u -> v) = 0  if elev(v) < elev(u)   (downhill: you roll for free)
    cost(u -> v) = 1  otherwise               (flat or uphill: you have to push)

So the cost of a route is the number of pushes it takes, and the shortest
path is the route with the fewest pushes. The proposal phrased the weights the
other way round (downhill = 1); we flipped them so that "shortest path" and
"best Heelys route" mean the same thing. See the progress report, section (a).

Node indexing: node (row r, column c) has index r * n + c.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field


def edge_cost(elev_u: float, elev_v: float) -> int:
    """Cost of travelling from a node at elevation elev_u to one at elev_v."""
    return 0 if elev_v < elev_u else 1


@dataclass
class Graph:
    """A directed graph with 0/1 edge costs laid out on an n x n grid.

    adj[u] is a list of (v, cost) pairs for edges u -> v.
    """

    n: int
    elev: list[float]
    adj: list[list[tuple[int, int]]] = field(repr=False)

    @property
    def V(self) -> int:
        return self.n * self.n

    @property
    def E(self) -> int:
        return sum(len(a) for a in self.adj)

    def node(self, r: int, c: int) -> int:
        return r * self.n + c

    def rc(self, u: int) -> tuple[int, int]:
        return divmod(u, self.n)

    def cost(self, u: int, v: int) -> int:
        """Cost of the edge u -> v. Raises KeyError if there is no such edge."""
        for x, w in self.adj[u]:
            if x == v:
                return w
        raise KeyError(f"no edge {u} -> {v}")

    def path_cost(self, path: list[int]) -> int:
        """Total cost of a path given as a list of node indices."""
        return sum(self.cost(path[i], path[i + 1]) for i in range(len(path) - 1))


def make_terrain(n: int, seed: int = 0, n_hills: int | None = None) -> list[float]:
    """Smooth random terrain: a sum of Gaussian hills (and a few valleys).

    Deterministic for a given (n, seed) so experiments can be reproduced.
    """
    rng = random.Random(seed)
    if n_hills is None:
        n_hills = max(3, n // 8)
    hills = []
    for _ in range(n_hills):
        cx, cy = rng.uniform(0, n - 1), rng.uniform(0, n - 1)
        sigma = rng.uniform(0.12 * n, 0.35 * n)
        height = rng.uniform(0.5, 1.0) * (1.0 if rng.random() < 0.7 else -1.0)
        hills.append((cx, cy, 2.0 * sigma * sigma, height))

    elev = [0.0] * (n * n)
    for r in range(n):
        for c in range(n):
            z = 0.0
            for cx, cy, two_sigma_sq, h in hills:
                z += h * math.exp(-((r - cx) ** 2 + (c - cy) ** 2) / two_sigma_sq)
            elev[r * n + c] = z
    return elev


def graph_from_elevation(n: int, elev: list[float]) -> Graph:
    """Build the 4-neighbour directed grid graph from an elevation list."""
    if len(elev) != n * n:
        raise ValueError(f"expected {n * n} elevations, got {len(elev)}")
    adj: list[list[tuple[int, int]]] = [[] for _ in range(n * n)]
    for r in range(n):
        for c in range(n):
            u = r * n + c
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                rr, cc = r + dr, c + dc
                if 0 <= rr < n and 0 <= cc < n:
                    v = rr * n + cc
                    w = edge_cost(elev[u], elev[v])
                    adj[u].append((v, w))
    return Graph(n=n, elev=elev, adj=adj)


def make_grid(n: int, seed: int = 0) -> Graph:
    """Generate a random hilly n x n world. Same (n, seed) -> same world."""
    return graph_from_elevation(n, make_terrain(n, seed))
