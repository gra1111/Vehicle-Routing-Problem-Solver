"""Parser for Solomon benchmark instances.

Reads the standard Solomon ``.txt`` format (vehicle count/capacity header
followed by the customer table) and returns an ``Instance``.
"""

from __future__ import annotations

from cvrptw.model import Instance, Node


def parse_solomon(path: str) -> Instance:
    """read a solomon benchmark txt file and build an instance

    path: path to the solomon .txt file

    Returns
    an instance built from the file
    """
    with open(path) as file:
        lines = file.readlines()

    rows = []
    for line in lines:
        clean = line.strip()
        if clean:
            rows.append(clean)

    name = rows[0]

    # number of vehicles and capacity sit right below the NUMBER CAPACITY header
    capacity = 0.0
    num_vehicles = None
    for i in range(len(rows)):
        if rows[i].startswith("NUMBER"):
            header_values = rows[i + 1].split()
            num_vehicles = int(header_values[0])
            capacity = float(header_values[1])
            break

    nodes = []
    for row in rows:
        parts = row.split()
        if len(parts) >= 7 and parts[0].isdigit():
            index = int(parts[0])
            x = float(parts[1])
            y = float(parts[2])
            demand = float(parts[3])
            start_time = float(parts[4])
            end_time = float(parts[5])
            service_time = float(parts[6])
            nodes.append(Node(index, x, y, demand,
                         start_time, end_time, service_time))

    return Instance(name, capacity, nodes, num_vehicles)
