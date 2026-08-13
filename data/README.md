# Data

Benchmark instances used to evaluate the solvers. This is **third-party
benchmark data**, not original work

## `solomon/` — Solomon VRPTW benchmark (1987)

The classic 56 instances, each with a depot and 100 customers. They come with
published best-known / optimal solutions, which makes them ideal for measuring
solver quality

| Family | Files | Customer layout | Time windows |
|--------|-------|-----------------|--------------|
| C1 | c101–c109 | clustered | tight |
| C2 | c201–c208 | clustered | wide |
| R1 | r101–r112 | random | tight |
| R2 | r201–r211 | random | wide |
| RC1 | rc101–rc108 | random + clustered | tight |
| RC2 | rc201–rc208 | random + clustered | wide |

### File format

Each `.txt` file holds:

- line 1: the instance name
- a `VEHICLE` block with the number of vehicles and the vehicle capacity
- a `CUSTOMER` block, one row per node:
  `cust_no  x  y  demand  ready_time  due_date  service_time`
- node `0` is the depot; `ready_time` / `due_date` map to `start_time` /
  `end_time` in `cvrptw.model.Node`

Parsed by `cvrptw/parser.py` (`parse_solomon`)

## Source and attribution

- Original benchmark: Marius M. Solomon (1987) *Algorithms for the Vehicle
  Routing and Scheduling Problems with Time Window Constraints*
- Reference portal (best-known solutions): SINTEF Transportation Optimization
  Portal https://www.sintef.no/projectweb/top/vrptw/
- Files in this repo were obtained from a public mirror of the original
  Solomon format

These files are redistributed here only for convenience and reproducibility, all credit for the instances belongs to the original authors.
