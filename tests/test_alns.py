"""tests for the alns"""

import random

from cvrptw.parser import parse_solomon
from cvrptw.model import Node, Instance, Solution
from cvrptw.heuristics.construction import build_initial_solution
from cvrptw.heuristics.alns import random_removal, worst_removal, greedy_repair, regret_repair, solve


def flat_customers(routes):
    return sorted(c for route in routes for c in route)


def test_random_removal():
    instance = parse_solomon('data/solomon/c101.txt')
    initial = build_initial_solution(instance)
    rng = random.Random(0)

    before = flat_customers(initial.routes)
    pruned, removed = random_removal(instance, initial.routes, 5, rng)

    # removes exactly n
    assert len(removed) == 5

    assert sorted(flat_customers(pruned) + removed) == before

    assert flat_customers(initial.routes) == before


def test_worst_removal():
    instance = parse_solomon('data/solomon/c101.txt')
    initial = build_initial_solution(instance)
    rng = random.Random(0)

    before = flat_customers(initial.routes)
    pruned, removed = worst_removal(instance, initial.routes, 5, rng)

    assert len(removed) == 5
    assert sorted(flat_customers(pruned) + removed) == before
    assert flat_customers(initial.routes) == before


def test_greedy_repair():
    instance = parse_solomon('data/solomon/c101.txt')
    initial = build_initial_solution(instance)
    rng = random.Random(0)

    pruned, removed = random_removal(instance, initial.routes, 5, rng)
    repaired = greedy_repair(instance, pruned, removed)

    assert flat_customers(repaired) == list(range(1, instance.size))


def test_regret():
    # on a real instance: coverage + feasibility
    instance = parse_solomon('data/solomon/c101.txt')
    initial = build_initial_solution(instance)
    rng = random.Random(0)

    pruned, removed = random_removal(instance, initial.routes, 5, rng)
    repaired = regret_repair(instance, pruned, removed)

    assert flat_customers(repaired) == list(range(1, instance.size))
    assert Solution(instance, repaired).is_feasible() is True

    depot = Node(0, 0, 0, 0, 0, 1000, 0)
    n1 = Node(1, 10, 0, 1, 0, 1000, 0)
    n2 = Node(2, 11, 0, 1, 0, 1000, 0)
    n3 = Node(3, 0, 10, 1, 0, 1000, 0)
    n4 = Node(4, 0, 11, 1, 0, 1000, 0)
    toy = Instance('test_regret', 100, [depot, n1, n2, n3, n4])

    repaired = regret_repair(toy, [[1], [3, 4]], [2])
    route_with_2 = next(route for route in repaired if 2 in route)
    assert 1 in route_with_2


def test_solve():
    instance = parse_solomon('data/solomon/c101.txt')
    initial = build_initial_solution(instance)
    best = solve(instance, 100, 20, 0)

    # feasible and complete
    assert best.is_feasible() is True
    assert flat_customers(best.routes) == list(range(1, instance.size))
    # improves or ties the construction
    assert best.distance() <= initial.distance()
    # deterministic with seed
    again = solve(instance, 100, 20, 0)
    assert best.distance() == again.distance()
