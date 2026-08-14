"""construction heuristic for an initial feasible solution using a greedy aproach for simplicity
"""

from cvrptw.model import Instance, Solution
from cvrptw.evaluation import route_demand, route_distance


def best_node_insertion(instance: Instance, route: list[int], customer_idx: int):
    """find the cheapest feasible position to insert a customer tying every position

    instance: the problem instance
    route: the current route (without depot)
    customer: customer index

    Returns
    (position, extra_cost) or None if the customer does not fit anywhere
    """
    base = route_distance(instance, route)
    base_demand = route_demand(instance, route)

    best = None
    for i in range(len(route) + 1):
        if base_demand + instance.nodes[customer_idx].demand <= instance.vehicle_capacity:
            new_route = route[:i] + [customer_idx] + route[i:]
            extra = route_distance(instance, new_route) - base
            if best is None or extra < best[1]:
                best = (i, extra)
    return best


def build_initial_solution(instance: Instance) -> Solution:
    """build a starting solution by greedy insertion 

    instance: the problem instance

    Returns
    a feasible complete solution
    """
    return None
