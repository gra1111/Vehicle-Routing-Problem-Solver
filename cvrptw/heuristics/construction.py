"""construction heuristic for an initial feasible solution using a greedy aproach for simplicity
"""

from cvrptw.model import Instance, Solution


def best_node_insertion(instance: Instance, route: list[int], customer_idx: int):
    """find the cheapest feasible position to insert a customer tying every position

    instance: the problem instance
    route: the current route (without depot)
    customer: customer index

    Returns
    (position, extra_cost) or None if the customer does not fit anywhere
    """
    nodes = instance.nodes
    dist = instance.distances

    # check capacity first
    total_demand = nodes[customer_idx].demand
    for i in route:
        total_demand += nodes[i].demand
    if total_demand > instance.vehicle_capacity:
        return

    final_end_time = nodes[0].end_time

    # assume the input route is feasible and calcualte the forward pass ie what time do I come out of eavery node in the route
    departures = [0.0]
    previous_idx = 0
    time_i = 0.0
    for i in range(len(route)):
        current_idx = route[i]
        node = nodes[current_idx]
        # time fo arrivla
        arrival = time_i + dist[previous_idx][current_idx]
        # if arraived before start time then went till start time
        service_start = arrival if arrival > node.start_time else node.start_time
        time_i = service_start + node.service_time
        departures.append(time_i)
        previous_idx = current_idx

    # backward pass ie latest arrival at each node that keeps the route possible
    latest_arrivals = [final_end_time]
    for i in range(len(route) - 1, -1, -1):
        current_idx = route[i]
        node = nodes[current_idx]
        if i+1 < len(route):
            next_index = route[i+1]
        else:
            next_index = 0
        # latest that can be arrievd to node i based on what the next nodes (i+1,...) need
        latest_posible = latest_arrivals[-1] - \
            node.service_time - dist[current_idx][next_index]
        # min between latest that you can arrive and the end time of the node
        latest_arrivals.append(min(latest_posible, node.end_time))
    # to keep in the right order
    latest_arrivals.reverse()

    best = None
    for i in range(len(route) + 1):
        previous_idx = route[i - 1] if i > 0 else 0
        next_node = route[i] if i < len(route) else 0

        arrival_new_node = departures[i] + dist[previous_idx][customer_idx]
        service_new_node = arrival_new_node if arrival_new_node > nodes[
            customer_idx].start_time else nodes[customer_idx].start_time
        if service_new_node < nodes[customer_idx].end_time:
            arrival_next = service_new_node + \
                nodes[customer_idx].service_time + \
                dist[customer_idx][next_node]
            if arrival_next < latest_arrivals[i]:
                extra = (dist[previous_idx][customer_idx] + dist[customer_idx][next_node]
                         - dist[previous_idx][next_node])
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
