"""adaptive large neighborhood search
"""

import random
from cvrptw.model import Instance, Solution
from cvrptw.heuristics.construction import build_initial_solution, best_node_insertion


def random_removal(routes, n, rng_state):
    """remove n random customers from the routes

    routes: current routes (list of lists of customer indices)
    n: how many customers to remove
    rng_state: a random.Random object for reproducibility

    Returns
    (removed_routes, removed) the routes without the removed customers and the removed customers list
    """
    flat_route = [i for route in routes for i in route]
    removed = rng_state.sample(flat_route, n)

    removed_routes = [[c for c in route if c not in removed]
                      for route in routes]

    return removed_routes, removed


def greedy_repair(instance, routes, removed):
    """reinsert the removed customers with a greedy aproach

    instance: the problem instance
    routes: the partial routes after the removal
    removed: the customers to reinsert

    Returns
    the repaired routes covering all customers again
    """
    best_routes = routes.copy()
    for removed_customer in removed:
        best_route = None
        best_pos = None  # position, extra_cost
        for route in best_routes:
            best_insertion = best_node_insertion(
                instance, route, removed_customer)
            if best_insertion is not None:
                position, extra_cost = best_insertion
                if best_route == None or extra_cost < best_pos[1]:
                    best_route = route
                    best_pos = (position, extra_cost)
        if best_route == None:
            best_routes.append([removed_customer])

        else:
            # use insert for inplace modifications
            best_route.insert(best_pos[0], removed_customer)

    return best_routes


def solve(instance, iterations=1000, n=20, seed=0):
    """solve a cvrptw instance with alns

    starts from the greedy construction and repeats destroy plus repair keeping
    the best solution found a candidate is accepted only if it is better than
    the current solution

    instance: the problem instance
    iterations: how many destroy plus repair rounds to run
    n: how many customers to remove each round
    seed: seed for reproducibility

    Returns
    the best Solution found
    """
    rng_state = random.Random(seed)
    current_solution = build_initial_solution(instance)
    for _ in range(iterations):
        removed_routes, removed = random_removal(
            current_solution.routes, n, rng_state)
        candidate_routes = greedy_repair(instance, removed_routes, removed)
        candidate_solution = Solution(instance, candidate_routes)
        if candidate_solution.distance() < current_solution.distance():
            current_solution = candidate_solution
    return current_solution
