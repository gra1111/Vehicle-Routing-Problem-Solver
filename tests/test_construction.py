"""tests for the construction heuristic"""

from cvrptw.parser import parse_solomon
from cvrptw.model import Node, Instance
from cvrptw.heuristics.construction import build_initial_solution, best_node_insertion


def test_build_initial_solution():
    instance = parse_solomon('data/solomon/c101.txt')
    solution = build_initial_solution(instance)

    # covers every customer exactly once
    assert sorted(solution.visited_customers) == list(range(1, instance.size))
    # feasibility
    assert solution.is_feasible() is True


def test_best_node_insertion():
    instance = parse_solomon('data/solomon/c101.txt')

    # empty route scenario
    result = best_node_insertion(instance, [], 1)
    assert result is not None
    position, _ = result
    assert position == 0

    nodes = [Node(0, 0, 0, 0, 0, 100, 0), Node(
        1, 1, 0, 8, 0, 100, 0), Node(2, 2, 0, 8, 0, 100, 0)]
    instance_rejects = Instance('test_rejects_best_insertion', 10, nodes)
    assert best_node_insertion(instance_rejects, [1], 2) is None
