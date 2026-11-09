# Heely-Analysis

CS 351 Analysis of Algorithms, Fall 2026. Team: The Wheel Ones (Conor Vahey, Felicity Chin, Oscar Yaun).

Routing a Heelys rider across a hilly map with Dijkstra's algorithm. Rolling downhill
costs 0 and every flat or uphill step costs 1 (one "push"); the best route has the
fewest pushes. ALT (A*, Landmarks, Triangle inequality) will be added next.

## Build

Python 3.10 or newer. No build step. Install the two dependencies (matplotlib for the
plot, pytest for the tests):

```
pip install -r requirements.txt
```

## Run the tests

```
python -m pytest -q
```

10 tests, under a second: a hand-built world with known answers, Dijkstra vs trying
every possible path on tiny worlds, a direct check that Dijkstra's distances are
optimal on larger worlds, and a check that every returned route is a real path with
the reported cost.

## Reproduce the preliminary plot

```
python -m heely.experiment      # ~3 s. Writes results/queries.csv
python -m heely.plot            # Writes results/preliminary_plot.png
```

3 random worlds at each of 7 sizes (100 to 10,000 nodes), 20 random queries per world.
Worlds and queries are seeded, so the CSV is reproducible (timings will differ by machine).

## Layout

```
heely/graph.py        world generator: n x n grid, random elevation, 0/1 edge costs
heely/dijkstra.py     Dijkstra with a binary heap
heely/experiment.py   timing harness -> results/queries.csv
heely/plot.py         results/queries.csv -> results/preliminary_plot.png
tests/                pytest suite (includes the brute-force check)
report/               checkpoint progress report and analysis draft
```
