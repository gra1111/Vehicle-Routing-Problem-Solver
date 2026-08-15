"""tests for the construction heuristic"""

from cvrptw.parser import parse_solomon
from cvrptw.model import Node, Instance
from cvrptw.heuristics.construction import build_initial_solution, best_node_insertion
from cvrptw.evaluation import is_feasible


def test_covers_all_customers_once():
    instance = parse_solomon('data/solomon/c101.txt')
    solution = build_initial_solution(instance)

    visited = sorted(solution.visited_customers)
    expected = list(range(1, instance.size))
    assert visited == expected


def test_feasible():
    instance = parse_solomon('data/solomon/c101.txt')
    solution = build_initial_solution(instance)

    assert is_feasible(instance, solution) is True


def test_best_insertion_empty_route():
    instance = parse_solomon('data/solomon/c101.txt')

    result = best_node_insertion(instance, [], 1)

    assert result is not None
    position, _ = result
    assert position == 0


def test_rejects_best_insertion():
    nodes = [Node(0, 0, 0, 0, 0, 100, 0), Node(
        1, 1, 0, 8, 0, 100, 0), Node(2, 2, 0, 8, 0, 100, 0)]
    instance = Instance('test_rejects_best_insertion', 10, nodes)
    result = best_node_insertion(instance, [1], 2)

    assert result is None
