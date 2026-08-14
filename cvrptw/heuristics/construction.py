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

    # if the new demand exceeds the vehicle capacity the node cannot be inserted
    if base_demand + instance.nodes[customer_idx].demand > instance.vehicle_capacity:
        return None
    best = None
    for i in range(len(route) + 1):
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
    nodes = list(range(1, instance.size))
    routes = []

    while nodes:
        # start the route with the farder node from the depot
        further = nodes[0]
        for i in nodes:
            if instance.distance(0, i) > instance.distance(0, further):
                further = i
        route = [further]
        nodes.remove(further)

        # keep inserting nodes with the cheapest distance cost
        while node_pick != None:
            node_pick = None
            for i in nodes:
                result = best_node_insertion(instance, route, i)
                if result is not None:
                    pos, extra = result
                    if node_pick is None or extra < node_pick[2]:
                        node_pick = (i, pos, extra)
            i, pos, extra = node_pick
            route.insert(pos, i)
            nodes.remove(i)
        routes.append(route)

    return Solution(instance, routes)
