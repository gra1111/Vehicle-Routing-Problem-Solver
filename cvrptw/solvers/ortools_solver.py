"""wrapper around google or-tools routing solver

translates an instance into an or-tools like routing model and solves it and translates back into the solution class so its comparable to our alns solver

important to note that we want th objective to be pure distance (not minimizin number of vehicles) so it aligns to out alns

based on the or-tools routing guide adapted for real valued solomon distances (integer scaling) and customer service times
https://developers.google.com/optimization/routing/cvrp
https://developers.google.com/optimization/routing/vrptw
"""

from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from cvrptw.model import Instance, Solution


# we need to scale everything because we work in floats and ortools works in integers
scale = 100


def solve(instance: Instance, num_vehicles=None, time_limit=5) -> Solution:
    """solve a cvrptw instance with or-tools
    to do this I followed the documention on google and adapted it to my data formats

    instance: the problem instance
    num_vehicles: how many vehicles are available (defaults to the instance value)
    time_limit: seconds the local search is allowed to run

    Returns
    the best Solution found or None if or-tools finds nothing feasible
    """
    size = instance.size
    if num_vehicles is None:
        num_vehicles = instance.num_vehicles or (size - 1)
    depot = 0

    nodes = instance.nodes
    distances = instance.distances

    manager = pywrapcp.RoutingIndexManager(size, num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)

    # objective, total travelled distance
    # almost identical function to the one defined on the orttools docs
    def distance_callback(from_index, to_index):
        i = manager.IndexToNode(from_index)
        j = manager.IndexToNode(to_index)
        return round(distances[i][j] * scale)
    distance_idx = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(distance_idx)

    # capacity constraint
    def demand_callback(from_index):
        i = manager.IndexToNode(from_index)
        return int(nodes[i].demand)

    demand_idx = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_idx,
        0,
        [int(instance.vehicle_capacity)] * num_vehicles,
        True,
        'Capacity',
    )

    # the transiit time is the service time of the node we leave plus the travel
    def time_callback(from_index, to_index):
        i = manager.IndexToNode(from_index)
        j = manager.IndexToNode(to_index)
        return round((nodes[i].service_time + distances[i][j]) * scale)

    time_idx = routing.RegisterTransitCallback(time_callback)
    horizon = round(instance.depot.end_time * scale)
    routing.AddDimension(
        time_idx,
        horizon,
        horizon,
        True,
        'Time',
    )
    time_dimension = routing.GetDimensionOrDie('Time')

    # each customer must start service inside its window
    for node in nodes:
        if node.index == depot:
            continue
        index = manager.NodeToIndex(node.index)
        time_dimension.CumulVar(index).SetRange(
            round(node.start_time * scale), round(node.end_time * scale))

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)
    params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    params.time_limit.FromSeconds(time_limit)

    solution = routing.SolveWithParameters(params)
    if solution is None:
        return None

    # create our Solution instance
    routes = []
    for vehicle in range(num_vehicles):
        index = routing.Start(vehicle)
        route = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            if node != depot:
                route.append(node)
            index = solution.Value(routing.NextVar(index))
        if route:
            routes.append(route)

    return Solution(instance, routes)
