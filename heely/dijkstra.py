"""Dijkstra's algorithm with a binary heap (Python's heapq) and lazy deletion."""

from __future__ import annotations

import heapq
from dataclasses import dataclass

from .graph import Graph

INF = float("inf")


@dataclass
class QueryResult:
    cost: float            # cost of the best route s -> t (number of pushes)
    path: list[int]        # node indices from s to t inclusive
    settled: int           # nodes popped from the heap and finalised
    relaxed: int           # edge relaxations attempted


def dijkstra(adj: list[list[tuple[int, int]]], s: int, t: int | None = None):
    """Run Dijkstra from s over an adjacency list.

    Returns (dist, parent, settled, relaxed). If t is given, the search stops
    as soon as t is settled. If t is None the full single-source tree is computed.
    """
    n = len(adj)
    dist = [INF] * n
    parent = [-1] * n
    done = [False] * n
    dist[s] = 0
    heap = [(0, s)]
    settled = 0
    relaxed = 0
    while heap:
        d, u = heapq.heappop(heap)
        if done[u]:
            continue            # stale entry: u was already settled at a lower key
        done[u] = True
        settled += 1
        if u == t:
            break
        for v, w in adj[u]:
            relaxed += 1
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                parent[v] = u
                heapq.heappush(heap, (nd, v))
    return dist, parent, settled, relaxed


def reconstruct(parent: list[int], s: int, t: int) -> list[int]:
    """Walk parent pointers back from t to s."""
    path = [t]
    while path[-1] != s:
        p = parent[path[-1]]
        if p == -1:
            return []       # t unreachable
        path.append(p)
    path.reverse()
    return path


def shortest_path(g: Graph, s: int, t: int) -> QueryResult:
    """Fewest-pushes route from s to t using Dijkstra."""
    dist, parent, settled, relaxed = dijkstra(g.adj, s, t)
    return QueryResult(cost=dist[t], path=reconstruct(parent, s, t),
                       settled=settled, relaxed=relaxed)
