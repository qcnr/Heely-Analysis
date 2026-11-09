from __future__ import annotations

import heapq
from dataclasses import dataclass

from graph import Graph

INF = float("inf")

#holds cost of best route, the path of best route, nodes popped from heap and settled, and amount of edge relaxations
@dataclass
class QueryResult:
    cost: float
    path: list[int]
    settled: int
    relaxed: int

#modified version of dijkstra from out last homework folder
def dijkstra(adj: list[list[tuple[int, int]]], s: int, t: int | None = None):
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
            continue #if stale node where shortest path already exists
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

#recreates path once we have a shortest path 
def reconstruct(parent: list[int], s: int, t: int) -> list[int]:
    path = [t]
    while path[-1] != s:
        p = parent[path[-1]]
        if p == -1:
            return [] #end of thing
        path.append(p)
    path.reverse()
    return path

#the function called in other files that runs dijkstra and returns the shortest path
def shortest_path(g: Graph, s: int, t: int) -> QueryResult:
    dist, parent, settled, relaxed = dijkstra(g.adj, s, t)
    return QueryResult(cost=dist[t], path=reconstruct(parent, s, t),
                       settled=settled, relaxed=relaxed)
