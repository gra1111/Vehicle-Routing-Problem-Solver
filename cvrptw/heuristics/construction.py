"""construction heuristic for an initial feasible solution using a greedy aproach for simplicity
"""

from cvrptw.model import Instance, Solution
from cvrptw.evaluation import is_route_feasible


def best_node_insertion(instance: Instance, route: list[int], customer_idx: int):
    """find the cheapest feasible position to insert a customer tying every position

    instance: the problem instance
    route: the current route (without depot)
    customer: customer index

    Returns
    (position, extra_cost) or None if the customer does not fit anywhere
    """

    best = None
    for i in range(len(route) + 1):
        new_route = route[:i] + [customer_idx] + route[i:]
        if is_route_feasible(instance, new_route):
            previous_node = route[i - 1] if i > 0 else 0
            next_node = route[i] if i < len(route) else 0
            extra = (instance.distance(previous_node, customer_idx) + instance.distance(
                customer_idx, next_node) - instance.distance(previous_node, next_node))
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
        # start the route with the further node from the depot
        further = nodes[0]
        for i in nodes:
            if instance.distance(0, i) > instance.distance(0, further):
                further = i
        route = [further]
        nodes.remove(further)

        # keep inserting nodes with the cheapest distance cost
        inserting = True
        while inserting:
            node_pick = None
            for i in nodes:
                result = best_node_insertion(instance, route, i)
                if result is not None:
                    pos, extra = result
                    if node_pick is None or extra < node_pick[2]:
                        node_pick = (i, pos, extra)
            if node_pick is None:
                inserting = False
            else:
                i, pos, extra = node_pick
                route.insert(pos, i)
                nodes.remove(i)
        routes.append(route)

    return Solution(instance, routes)
