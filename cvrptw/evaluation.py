"""Cost computation and feasibility checking.

The single source of truth for evaluating any solution, regardless of which
solver produced it. Every solver's output is validated here before its
results are trusted or reported.

TODO (M1): implement the empty functions below.
"""

from __future__ import annotations

from cvrptw.model import Instance, Solution


def route_distance(instance: Instance, route: list[int]) -> float:
    """Total travelled distance of a single route.

    instance: the problem instance
    route: customer indices in visit order

    Returns
    The sum of distances.
    """
    if not len(route):
        return 0
    d = instance.distances[0][route[0]]
    for i in range(1, len(route)):
        d += instance.distances[route[i-1]][route[i]]
    d += instance.distances[route[-1]][0]

    return d


def solution_distance(instance: Instance, solution: Solution) -> float:
    """Total travelled distance of a whole solution.

    instance: the problem instance.
    solution: the candidate solution (set of routes).

    Returns
    The total distance across all routes.
    """
    return sum(route_distance(instance, route) for route in solution.routes)


def route_demand(instance: Instance, route: list[int]) -> float:
    """total demand served by a single route used to check the vehicle capacity constraint

    instance: the problem instance
    route: customer indices in visit order

    Returns
    the sum of customer demands on the route
    """
    total = 0.0
    for c in route:
        total += instance.nodes[c].demand

    return total


def is_route_feasible(instance: Instance, route: list[int]) -> bool:
    """whether a single route satisfies capacity and time windows

    instance: the problem instance
    route: customer indices in visit order

    Returns
    true if the route respects capacity and timeline
    """
    if not len(route):
        return True

    # capacity check
    if route_demand(instance, route) > instance.vehicle_capacity:
        return False

    # check timeline is consistent
    time = 0.0
    prev = 0
    for current in route:
        node = instance.nodes[current]
        arrival = time + instance.travel_time(prev, current)
        service_start = max(arrival, node.start_time)
        if service_start > node.end_time:
            return False
        time = service_start + node.service_time
        prev = current

    # check come back to depot in time
    back_to_depot = time + instance.travel_time(prev, 0)
    if back_to_depot > instance.depot.end_time:
        return False

    return True


def is_feasible(instance: Instance, solution: Solution) -> bool:
    """whether a whole solution is feasible

    instance: the problem instance
    solution: the candidate solution

    Returns
    true if the solution satisfies coverage and all per route constraints
    """
    # every customer visisted exactly once
    visited = solution.visited_customers
    expected = list(range(1, instance.size))
    if sorted(visited) != expected:
        return False

    # every route is feasible
    for route in solution.routes:
        if not is_route_feasible(instance, route):
            return False

    return True
