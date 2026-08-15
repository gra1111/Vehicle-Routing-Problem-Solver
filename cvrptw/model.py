"""Core data structures for the CVRPTW.

Defines the problem instance (customers, depot, demands, time windows,
vehicle capacity) and the solution (set of routes). Everything else in the
package is built on top of these types.

Conventions
-----------
- Node 0 is always the depot.
- A route is stored as a list of customer indices, WITHOUT the depot; the
  depot at the start and end of every route is implied.
- Following the Solomon benchmarks, the travel time between two nodes equals
  the Euclidean distance between them (see ``Instance.travel_time``).
"""

from __future__ import annotations

import math
from functools import cached_property


class Node:
    """A single location: the depot (index 0) or a customer.

    index: position of the node in the instance (0 = depot).
    x, y: planar coordinates (used for Euclidean distance/time).
    demand: quantity to deliver (0 for the depot).
    start_time: earliest time service may start (time window opens).
    end_time: latest time service may start (time window closes).
    service_time: time spent servicing the node.
    """

    def __init__(
        self,
        index: int,
        x: float,
        y: float,
        demand: float,
        start_time: float,
        end_time: float,
        service_time: float,
    ) -> None:
        self.index = index
        self.x = x
        self.y = y
        self.demand = demand
        self.start_time = start_time
        self.end_time = end_time
        self.service_time = service_time

    @property
    def is_depot(self) -> bool:
        return self.index == 0

    def __repr__(self) -> str:
        return (
            f"Node(index={self.index}, x={self.x}, y={self.y}, "
            f"demand={self.demand}, start_time={self.start_time}, "
            f"end_time={self.end_time}, service_time={self.service_time})"
        )


class Instance:
    """
    nodes[0] is the depot; nodes[1:] are the customers. The distance
    matrix is computed once, lazily, and cached.
    """

    def __init__(
        self,
        name: str,
        vehicle_capacity: float,
        nodes: list[Node],
        num_vehicles: int | None = None,
    ) -> None:
        self.name = name
        self.vehicle_capacity = vehicle_capacity
        self.nodes = nodes
        self.num_vehicles = num_vehicles

    @property
    def depot(self) -> Node:
        return self.nodes[0]

    @property
    def customers(self) -> list[Node]:
        return self.nodes[1:]

    @property
    def size(self) -> int:
        """Total number of nodes, depot included."""
        return len(self.nodes)

    @cached_property
    def distances(self) -> list[list[float]]:
        """Symmetric Euclidean distance matrix, indexed by node index."""
        n = len(self.nodes)
        matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            a = self.nodes[i]
            for j in range(i + 1, n):
                b = self.nodes[j]
                d = math.hypot(a.x - b.x, a.y - b.y)
                matrix[i][j] = d
                matrix[j][i] = d
        return matrix

    def distance(self, i: int, j: int) -> float:
        """Euclidean distance between node i and node j."""
        return self.distances[i][j]

    def travel_time(self, i: int, j: int) -> float:
        """Travel time between node i and node j.

        In the Solomon benchmarks travel time equals distance.
        """
        return self.distances[i][j]

    def __repr__(self) -> str:
        return (
            f"Instance(name={self.name!r}, vehicle_capacity="
            f"{self.vehicle_capacity}, size={self.size})"
        )


class Solution:
    """A candidate solution: a set of routes over an instance.

    Each route is a list of customer indices (no depot). An empty route means
    an unused vehicle and is ignored.
    """

    def __init__(self, instance: Instance, routes: list[list[int]]) -> None:
        self.instance = instance
        self.routes = routes

    @property
    def num_vehicles(self) -> int:
        """Number of routes that actually serve at least one customer."""
        return sum(1 for route in self.routes if route)

    @property
    def visited_customers(self) -> list[int]:
        """Flat list of all customer indices across all routes."""
        resultado = []
        for route in self.routes:
            for c in route:
                resultado.append(c)
        return resultado

    def distance(self) -> float:
        """total travelled distance over all the routes"""
        from cvrptw.evaluation import route_distance  # import here to avoid circular imports
        return sum(route_distance(self.instance, route) for route in self.routes)

    def is_feasible(self) -> bool:
        """whether every customer is visited once and every route is feasible"""
        from cvrptw.evaluation import is_route_feasible  # import here to avoid circular imports
        expected = list(range(1, self.instance.size))
        if sorted(self.visited_customers) != expected:
            return False
        for route in self.routes:
            if not is_route_feasible(self.instance, route):
                return False
        return True

    def __repr__(self) -> str:
        return f"Solution(num_vehicles={self.num_vehicles}, routes={self.routes})"
