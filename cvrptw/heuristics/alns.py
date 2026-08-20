"""adaptive large neighborhood search
"""

import numpy as np
import random
from cvrptw.model import Solution
from cvrptw.heuristics.construction import build_initial_solution, best_node_insertion


def random_removal(instance, routes, n, rng_state):
    """remove n random customers from the routes

    instance: the problem instance (not actually used, just to allign with worst_removal inputs)
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


def worst_removal(instance, routes, n, rng):
    """remove the n customers that add the most distance to their route

    for each customer compute its detour d(prev, c) + d(c, next) - d(prev, next)
    where prev and next are its neighbours in the route (the depot 0 at the ends)
    then remove the ones with the largest detour a small random factor avoids
    always removing exactly the same customers
    do not mutate the input routes work on a copy

    instance: the problem instance
    routes: current routes (list of lists of customer indices)
    n: how many customers to remove
    rng: a random.Random instance for reproducibility

    Returns
    (pruned_routes, removed) the routes without those customers and the removed list
    """

    # detour each costumer makes to the route
    costs = []
    for route in routes:
        for node_pos in range(len(route)):
            node = route[node_pos]
            if node_pos >= 1:
                prev = route[node_pos - 1]
            else:
                prev = 0
            if node_pos < len(route) - 1:
                nxt = route[node_pos + 1]
            else:
                nxt = 0
            node_cost = instance.distance(
                prev, node) + instance.distance(node, nxt) - instance.distance(prev, nxt)
            costs.append((node_cost, node))
    costs.sort(reverse=True)

    # p to biass the index towards 0 (worst nodes) (formula from Ropke & Pisinger)
    p = 3
    removed = []
    for _ in range(n):
        index = int(rng.random() ** p * len(costs))
        removed.append(costs.pop(index)[1])

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


def regret_repair(instance, routes, removed):
    """reinsert the removed customers using the regret criterion

    for each removed customer look at its cheapest insertion in every route
    the regret is the difference between its second best route cost and its
    best route cost insert first the customer with the largest regret at its
    best position a customer that only fits in one route gets a very high
    regret and one that fits nowhere opens a new route
    repeat until every removed customer is placed

    instance: the problem instance
    routes: the routes after the customers removal
    removed: the customers to add

    Returns
    the repaired routes
    """
    while removed != []:
        best_to_include = None  # (route, node, difference, pos)
        for node in removed:
            best = None
            second_best = None
            for route in routes:
                best_insertion = best_node_insertion(instance, route, node)
                if best_insertion != None:
                    pos, extra_cost = best_insertion
                    if best == None or extra_cost < best[1]:
                        second_best = best
                        best = (pos, extra_cost, route)
                    elif second_best == None or extra_cost < second_best[1]:
                        second_best = (pos, extra_cost, route)
            if second_best == None:
                # if second_best is None best is also None (high priority to include)
                if best == None:
                    routes.append([node])
                else:
                    best[2].insert(best[0], node)
                removed.remove(node)
                break
            difference = second_best[1]-best[1]
            if best_to_include == None or best_to_include[2] < difference:
                best_to_include = (best[2], node, difference, best[0])
        if best_to_include != None:
            best_to_include[0].insert(best_to_include[3], best_to_include[1])
            removed.remove(best_to_include[1])
    return routes


def solve(instance, iterations=1000, n=20, seed=0, early_stopping_n=30):
    """solve a cvrptw instance with alns

    instance: the problem instance
    iterations: how many destroy plus repair rounds to run
    n: how many customers to remove each round
    seed: seed for reproducibility
    early_stopping_n: stop early after this many iterations without a new best

    Returns
    (best Solution found, iteration where the search stopped)
    """
    weights = [[0.5, 0.5], [
        0.5, 0.5]]  # [greedy_repair_wight, regret_repair_weight], [random_removal_weight, worst_removal_weight]
    destroy_functions = [random_removal, worst_removal]
    repair_functions = [greedy_repair, regret_repair]

    # [greedy_repair_wight, regret_repair_weight], [random_removal_weight, worst_removal_weight]
    scores = [[0.0, 0.0], [0.0, 0.0]]

    # [greedy_repair_wight, regret_repair_weight], [random_removal_weight, worst_removal_weight]
    counts = [[0, 0], [0, 0]]
    points_1 = 3
    points_2 = 2
    points_3 = 1

    rng_state = random.Random(seed)
    current_solution = build_initial_solution(instance)
    best_solution = current_solution

    # number of iterations to update weights and percentage of the new weight to keep
    iterations_update = 100
    new_percentage = 15

    # T and coling for simulated annealing formula
    T = current_solution.distance() * 0.05
    coling = 0.995

    # early stopping
    no_improve = 0
    stopped_at = iterations
    for i in range(iterations):
        removal_choice = rng_state.choices(
            [0, 1], weights[1])[0]
        removed_routes, removed = destroy_functions[removal_choice](
            instance, current_solution.routes, n, rng_state)

        repair_choice = rng_state.choices(
            [0, 1], weights[0])[0]
        candidate_routes = repair_functions[repair_choice](
            instance, removed_routes, removed)
        # drop empty routes so the vehicle count stays honest
        candidate_routes = [route for route in candidate_routes if route]
        candidate_solution = Solution(instance, candidate_routes)

        # reward for being the best solution so far
        if candidate_solution.distance() < best_solution.distance():
            points = points_1
            current_solution = candidate_solution
            best_solution = candidate_solution
            no_improve = 0
        # reward for being beter that the current solution but not better than the best so far
        elif candidate_solution.distance() < current_solution.distance():
            points = points_3
            current_solution = candidate_solution
            no_improve += 1
        else:
            # simulated annealing
            delta = candidate_solution.distance() - current_solution.distance()
            acceptance_value = np.exp(-delta / T)
            # reaward for being chosen even if the solution is not better than the current solution
            if rng_state.random() < acceptance_value:
                points = points_2
                current_solution = candidate_solution
            else:
                # 0 reward for being discarded
                points = 0
            no_improve += 1

        scores[1][removal_choice] += points
        counts[1][removal_choice] += 1
        scores[0][repair_choice] += points
        counts[0][repair_choice] += 1
        T *= coling
        if (i + 1) % iterations_update == 0:
            # run through both repair and update and the 2 operators inside each
            for prob in range(2):
                for operator in range(2):
                    if counts[prob][operator] > 0:  # avoid divisions by 0
                        weights[prob][operator] = (100 - new_percentage)/100 * weights[prob][operator] + \
                            new_percentage/100 * \
                            (scores[prob][operator] / counts[prob][operator])
                    scores[prob][operator] = 0
                    counts[prob][operator] = 0

        # early stopping
        if no_improve >= early_stopping_n:
            stopped_at = i + 1
            break
    return best_solution, stopped_at
