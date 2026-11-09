"""generates a grid-world for our problem.

A world is an n x n grid of nodes where every node has an elevation and eachh node is
joined to its four grid neighbours by two directed edges (one each way), and
the cost of an edge depends on which way you are travelling along it

the cost function returns 0 if it's downhill and 1 if it's not downhill where 1 is considered a push ie you 
have to push to go forward. The shortest path is the one with the fewest pushes so the one with the least amount of
cost = 1.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

#determines whether downhill
def edge_cost(elev_u: float, elev_v: float) -> int:
    return 0 if elev_v < elev_u else 1

#is a nxn graph with costs of either 0 or 1 laid on on graph.
@dataclass
class Graph:

    n: int
    elev: list[float]
    adj: list[list[tuple[int, int]]] = field(repr=False) #each index of adj is the adjacent vertices and costs to them

    @property
    def V(self) -> int:
        return self.n * self.n #creat nxn grid

    @property
    def E(self) -> int:
        return sum(len(a) for a in self.adj)

    def node(self, r: int, c: int) -> int:
        return r * self.n + c

    def rc(self, u: int) -> tuple[int, int]:
        return divmod(u, self.n)

    #given there's an edge, gives the cost of that edge
    def cost(self, u: int, v: int) -> int:
        for x, w in self.adj[u]:
            if x == v:
                return w
        raise KeyError(f"no edge {u} -> {v}")

#total cost of path
    def path_cost(self, path: list[int]) -> int:
        return sum(self.cost(path[i], path[i + 1]) for i in range(len(path) - 1))

#super evil to make function :(
#generates a smooth random terrain and can be reproduced with a seed too
def make_terrain(n: int, seed: int = 0, n_hills: int | None = None) -> list[float]:
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

#uses make_terrain to graph it all
def graph_from_elevation(n: int, elev: list[float]) -> Graph:
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

#generates the grid, called for graphing and eventually plotting everything
def make_grid(n: int, seed: int = 0) -> Graph:
    return graph_from_elevation(n, make_terrain(n, seed))
