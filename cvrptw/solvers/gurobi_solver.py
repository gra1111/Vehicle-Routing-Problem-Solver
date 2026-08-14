"""gurobi solver for the cvrptw

builds the milp model with pyomo and solves it with gurobi
same formulation as the notebook notebooks/gurobi_cvrptw.ipynb
"""


import pyomo.environ as pe
import pyomo.opt as po

from cvrptw.model import Instance, Solution


def solve(instance: Instance, verbose: bool = False) -> Solution:
    """solve a cvrptw instance with gurobi

    instance: the problem instance
    verbose: if true shows the gurobi log

    Returns
    the best Solution found by gurobi
    """
    nodes = list(range(instance.size))
    customers = list(range(1, instance.size))

    # parameters
    c = instance.distances
    q = {i: instance.nodes[i].demand for i in nodes}
    a = {i: instance.nodes[i].start_time for i in nodes}
    b = {i: instance.nodes[i].end_time for i in nodes}
    s = {i: instance.nodes[i].service_time for i in nodes}
    Q = instance.vehicle_capacity

    # use the fleet size from the instance if it has one otherwise one vehicle per customer
    if instance.num_vehicles is not None:
        K = instance.num_vehicles
    else:
        K = len(customers)

    # all pairs of nodes connections and the ones that arrive at a customer
    links = [(i, j) for i in nodes for j in nodes if i != j]
    customer_links = [(i, j) for (i, j) in links if j != 0]

    # big-M (the worst case of the time constraint)
    M = max(b[i] for i in nodes) + max(s[i]
                                       for i in nodes) + max(c[i][j] for (i, j) in links)

    model = pe.ConcreteModel('cvrptw')

    # sets
    model.N = pe.Set(initialize=nodes, ordered=True)
    model.C = pe.Set(initialize=customers, ordered=True)
    model.L = pe.Set(initialize=links, dimen=2)

    # variables
    model.x = pe.Var(model.L, within=pe.Binary)

    def w_bounds(m, i):
        return (a[i], b[i])
    model.w = pe.Var(model.N, within=pe.NonNegativeReals, bounds=w_bounds)

    def u_bounds(m, i):
        return (q[i], Q)
    model.u = pe.Var(model.N, within=pe.NonNegativeReals, bounds=u_bounds)

    # the vehicle leaves the depot empty
    model.u[0].fix(0)

    # objective
    def obj_rule(m):
        return sum(c[i][j] * m.x[i, j] for (i, j) in m.L)
    model.obj = pe.Objective(rule=obj_rule, sense=pe.minimize)

    # 1  one link enters each customer j
    def in_customer_rule(m, j):
        return sum(m.x[i, j] for i in m.N if i != j) == 1
    model.in_customer = pe.Constraint(model.C, rule=in_customer_rule)

    # 2  one link leaves each customer i
    def out_customer_rule(m, i):
        return sum(m.x[i, j] for j in m.N if j != i) == 1
    model.out_customer = pe.Constraint(model.C, rule=out_customer_rule)

    # 3  no more than K vehicles leave and as many return as leave
    def depot_out_rule(m):
        return sum(m.x[0, j] for j in m.C) <= K
    model.depot_out = pe.Constraint(rule=depot_out_rule)

    def depot_balance_rule(m):
        return sum(m.x[0, j] for j in m.C) == sum(m.x[i, 0] for i in m.C)
    model.depot_balance = pe.Constraint(rule=depot_balance_rule)

    # 4  time propagation towards each customer j
    def time_rule(m, i, j):
        return m.w[i] + s[i] + c[i][j] - M * (1 - m.x[i, j]) <= m.w[j]
    model.time = pe.Constraint(customer_links, rule=time_rule)

    # 5  return to the depot before it closes
    def return_rule(m, i):
        return m.w[i] + s[i] + c[i][0] - M * (1 - m.x[i, 0]) <= b[0]
    model.return_depot = pe.Constraint(model.C, rule=return_rule)

    # 7  load propagation towards each customer j
    def load_rule(m, i, j):
        return m.u[i] + q[j] - Q * (1 - m.x[i, j]) <= m.u[j]
    model.capacity = pe.Constraint(customer_links, rule=load_rule)

    solver = po.SolverFactory('gurobi_direct')
    solver.solve(model, tee=verbose)

    # rebuild the routes from the active links
    active = [(i, j) for (i, j) in links if pe.value(model.x[i, j]) > 0.5]
    successors = {i: j for (i, j) in active if i != 0}
    routes = []
    for first in [j for (i, j) in active if i == 0]:
        route = [first]
        node = first
        while successors[node] != 0:
            node = successors[node]
            route.append(node)
        routes.append(route)

    return Solution(instance, routes)
