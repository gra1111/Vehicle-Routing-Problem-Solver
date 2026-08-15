# CVRPTW — Capacitated Vehicle Routing Problem with Time Windows (WIP)

Solving the CVRPTW and comparing different methods: an exact MILP model (Pyomo + Gurobi), a custom ALNS metaheuristic and an industry solver 

> Personal project, in active development. Not affiliated with any university course.

## Problem description

Given a depot, a number of vehicles with their respective capacity limits and customers with quantity demands and time windows we need to find the set of routes that serves everyone at a minimum total time (time = distance in our scenario).

This repo implements and compares different approaches under the same conditions: 
- **Exact**: a MILP formulation solved with Gurobi (via Pyomo). Guarantees the optimum but does not scale.
- **Heuristic**: a custom Adaptive Large Neighborhood Search (ALNS) that scales to large instances, trading the optimality guarantee for speed.
- **Industry solvers**: Wrappers around OR-Tools or VROOM for comparison.

## Status / roadmap

- [x] **M1 — Data & validation** Solomon parser, data model, cost + feasibility validators
- [x] **M2 — Gurobi MILP solver** 
[WIP] **M3 — Custom ALNS**
- [ ] **M4 — Industry solvers**
- [ ] **M5 — Experiments & analysis** 

Progress is tracked using [issues] and [milestones].

## A first result

The exact solver is optimal but its runtime explodes with instance size and structure. That gap is exactly what motivates the heuristic and metaheuristic. See `notebooks/gurobi_scaling.ipynb`.

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