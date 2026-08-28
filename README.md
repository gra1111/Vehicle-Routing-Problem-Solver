# CVRPTW — Capacitated Vehicle Routing Problem with Time Windows

Solving the CVRPTW and comparing different methods: an exact MILP model (Pyomo + Gurobi), a custom ALNS metaheuristic and an industry solver 

> Personal project

## Problem description

Given a depot, a number of vehicles with their respective capacity limits and customers with quantity demands and time windows we need to find the set of routes that serves everyone at a minimum total time (time = distance in our scenario).

This repo implements and compares different approaches under the same conditions: 
- **Exact**: a MILP formulation solved with Gurobi (via Pyomo). Guarantees the optimum but does not scale.
- **Heuristic**: a custom Adaptive Large Neighborhood Search (ALNS) that scales to large instances, trading the optimality guarantee for speed.
- **Industry solver**: A wrapper around Google OR-Tools for comparison.

## Results

The exact solver returns the optimum but its runtime explodes with instance size, so it only handles small instances (see `notebooks/gurobi_scaling.ipynb`). On a small sub-instance the custom ALNS reaches the same optimum as Gurobi. On full 100-customer instances, benchmarked on unseen instances and seeds, the ALNS is competitive with OR-Tools under the same time budget. Both minimise pure distance while the published best-known solutions minimise the number of vehicles first, so the gap to best-known can be negative ie a shorter distance obtained by using more vehicles. See `notebooks/comparison.ipynb`.

## Running it

Requires [uv](https://docs.astral.sh/uv/). The exact solver needs a Gurobi license (a free academic license works).

```bash
uv sync
uv run pytest
```

## References

- Solomon, M. M. (1987). *Algorithms for the Vehicle Routing and Scheduling Problems with Time Window Constraints.*
- Ropke, S. & Pisinger, D. (2006). *An Adaptive Large Neighborhood Search Heuristic for the Pickup and Delivery Problem with Time Windows.*

Benchmark instances belong to their original authors — see [`data/README.md`](data/README.md).