This project has been created as part of the 42 curriculum by ismonter.

Description
Fly-in Drones

Fly-in Drones is a pathfinding and simulation project developed as part of the 42 curriculum.

The goal of the project is to move a given number of drones from a starting hub to an ending hub in the fewest possible simulation turns, while respecting the constraints imposed by the network.

The network is represented as a graph composed of hubs and connections:

Hubs represent zones in the network.
Connections represent links between hubs.
Drones move through the network from the start hub to the end hub.
Hubs can have different zone types and capacities.
Connections can have a maximum number of drones that can use them simultaneously.

The project is divided into several main stages:

Parse and validate the input map.
Build an internal graph representation of the network.
Find all minimum-cost paths between the start and end hubs.
Find additional alternative paths with a cost of one or two turns above the minimum.
Generate different possible distributions of drones across these paths.
Simulate each distribution to determine how many turns it requires.
Select the distribution with the lowest number of turns.
Execute the selected strategy using the actual Drone objects.

The project also handles special movement rules such as restricted zones, which require two turns to reach, as well as hub and connection capacity limitations.

Features
Input file parsing and validation.
Support for an arbitrary number of drones.
Graph-based pathfinding.
Multiple minimum-cost paths.
Priority-zone preference when several paths have the same cost.
Alternative paths with minimum cost +1 and minimum cost +2.
Distribution of drones across multiple paths.
Turn-by-turn simulation.
Hub capacity management.
Connection capacity management.
Two-turn movement through restricted zones.
Strategic waiting when a movement cannot be performed.
Prevention of path conflicts and capacity violations.
Clear error messages for invalid configuration files.
Terminal output showing drone movements.
Algorithm
Graph representation

The network is represented as a graph.

Each Hub stores:

Its name.
Its coordinates.
Its type (start, end, or regular hub).
Its zone type (normal, restricted, priority, or blocked).
Its maximum drone capacity.
Its connections.

Each Connection stores:

Its source hub.
Its destination hub.
Its maximum simultaneous capacity.

Connections are treated as bidirectional when navigating the graph.

Pathfinding

The minimum-cost paths are calculated using a Dijkstra-based algorithm.

The cost of entering a hub depends on its zone type:

Zone type	Movement cost
normal	1
priority	1
restricted	2
blocked	Inaccessible

blocked hubs are excluded from navigation.

The pathfinding algorithm keeps track of both the minimum cost to reach every hub and the previous hubs that can produce that minimum cost. This allows the program to reconstruct all paths having the minimum cost, rather than keeping only one path.

When multiple minimum-cost paths exist, they are ordered according to the number of priority hubs they contain. Paths containing more priority zones are preferred.

Alternative paths

Finding only the shortest paths is not always enough to obtain the fastest overall simulation.

Several drones may compete for the same hubs or connections, creating bottlenecks. Because of this, the project also searches for paths whose cost is:

Minimum cost + 1.
Minimum cost + 2.

These paths can sometimes provide a better overall distribution of drones even though an individual drone takes a slightly more expensive route.

The search is bounded to paths whose cost does not exceed minimum_cost + 2.

Drone distribution

After obtaining the minimum-cost paths and the alternative paths, the program creates several candidate distributions.

The basic distribution assigns drones cyclically across the available paths. For example, if there are three available paths, drones are assigned approximately as:

Drone 1 -> Path 1
Drone 2 -> Path 2
Drone 3 -> Path 3
Drone 4 -> Path 1
Drone 5 -> Path 2
...


The program evaluates several combinations:

Only minimum-cost paths.
Minimum-cost paths + paths with cost +1.
Minimum-cost paths + one or more +1 paths.
Minimum-cost paths + paths with cost +2.

Each candidate distribution is passed to the simulation before the actual Drone objects are moved.

Simulation-based selection

For every candidate distribution, a separate simulation calculates how many turns are required to deliver all drones.

The simulation takes into account:

Hub occupancy.
Hub maximum capacity.
Connection capacity.
Drones leaving a hub during the current turn.
Drones entering a hub during the current turn.
Drones travelling through restricted zones.
Simultaneous movements.
Drones waiting when movement is not possible.

After all candidate distributions have been simulated, the program selects the distribution requiring the fewest turns.

This separates strategy selection from actual drone execution. The first simulation works with paths and positions rather than modifying the real Drone objects.

Final execution

Once the best distribution has been selected, it is assigned to the actual Drone objects.

The DroneController then performs the real simulation turn by turn.

For every turn, the controller:

Processes drones that are completing restricted-zone transit.
Checks the next possible movement for every remaining drone.
Checks hub and connection capacities.
Registers valid movements.
Executes the accepted movements.
Marks drones that reach the end hub as finished.
Produces the movement output.

This approach allows multiple drones to move simultaneously while respecting all capacity constraints.

Complexity and Efficiency

The pathfinding stage uses a Dijkstra-style algorithm. In the current implementation, the minimum-cost search uses a list of pending hubs and scans it to find the next minimum-cost hub, resulting in approximately O(V² + E) complexity, where:

V is the number of hubs.
E is the number of connections.

The implementation does not use a priority queue, because the project focuses on a manageable graph size and on keeping the algorithm explicit and easy to understand.

Path reconstruction can generate multiple paths when several previous hubs have the same minimum cost. Therefore, the number of paths can grow depending on the topology of the input graph.

Alternative path generation is bounded to paths up to two cost units above the minimum. Cycles are explicitly avoided while constructing these paths.

The simulation evaluates each candidate distribution independently. Its complexity depends mainly on:

The number of drones.
The number of turns required.
The number of candidate paths/distributions.

Paths are calculated once and then reused during the distribution and simulation stages rather than recalculating the shortest path for every drone.

This reduces unnecessary computation and allows the final controller to work with precomputed routes.

Input Format

The first line of the input file must define the number of drones:

nb_drones: 5


The configuration must contain exactly one start hub and one end hub:

start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]


Regular hubs can contain zone metadata:

hub: roof1 3 4 [zone=restricted color=red]
hub: roof2 6 2 [zone=normal color=blue]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
hub: obstacleX 5 5 [zone=blocked color=gray]


Connections are declared using:

connection: hub-roof1
connection: roof1-roof2
connection: corridorA-goal [max_link_capacity=2]


The parser validates:

The number of drones.
Hub names.
Coordinates.
Hub types.
Zone types.
Metadata syntax.
Hub capacities.
Connection capacities.
Duplicate hubs.
Duplicate connections.
Connections declared before their hubs.
The presence of exactly one start hub and one end hub.

Invalid configurations stop the program and produce an error describing the problem and, when applicable, the line where it occurred.

Installation

The project does not require external Python packages.

The only development tools used for code quality are:

flake8
mypy

They are not required to execute the program itself.

Python 3 is required.

Usage

Run the program with a map file:

python3 fly_in.py maps/easy/01_linear_path.txt


The input file must have the .txt extension.

The program validates the map, calculates the available routes, selects a drone distribution, and then executes the simulation.

Example output:

D1-hub D2-hub D3-hub
D1-goal D2-goal D3-goal


The exact output depends on the map, number of drones, capacities, and selected paths.

Project Structure
.
├── fly_in.py
├── parser.py
├── map.py
├── hub.py
├── connection.py
├── drone.py
├── pathfinding.py
├── simulation.py
├── drone_controller.py
└── maps/
    ├── easy/
    ├── medium/
    ├── hard/
    └── challenger/

Main modules

parser.py

Reads and validates the input configuration.

map.py

Builds the internal graph representation from the parsed configuration.

hub.py

Defines the Hub class and manages hub properties and connections.

connection.py

Defines connections between hubs and their capacity.

drone.py

Defines the Drone class and stores the state of each drone during the final simulation.

pathfinding.py

Implements the pathfinding algorithms and generates minimum-cost and alternative paths.

simulation.py

Evaluates candidate path distributions before the real drone simulation.

drone_controller.py

Coordinates the complete process and performs the final simulation using the Drone objects.

fly_in.py

Entry point of the program and command-line argument handling.

Visual Representation

The project provides a terminal-based visual representation of the simulation through movement output.

Each movement identifies the drone and its destination:

D1-hub
D2-hub
D3-goal


When a drone enters a restricted zone, the connection it is travelling through is represented:

D1-roof1-roof2


This representation allows the user to follow the simulation turn by turn and understand how drones are distributed throughout the network.

The terminal output is intentionally simple so that the movement strategy remains easy to follow, especially when several drones move simultaneously.

During development, additional debug output was also used to inspect candidate distributions, turn counts, hub occupancy, and drone movements. These debugging messages are not part of the intended final output.

Resources

The project was developed using the following types of resources:

Python documentation for language features, type hints, file handling, and data structures.
Documentation and learning resources about graph algorithms and Dijkstra's shortest-path algorithm.
General references about graph traversal, pathfinding, and shortest-path problems.
PEP 257 for Python docstring conventions.
flake8 documentation for Python style and linting.
mypy documentation for static type checking.
AI Usage

AI was used as a supporting tool during the development of this project.

It was mainly used for:

Reviewing design and implementation decisions.
Discussing algorithmic approaches and possible edge cases.
Reviewing the structure and organization of the project.
Helping prepare the README.md.
Helping write and improve Python docstrings according to PEP 257.
Reviewing explanations of the implemented algorithms and project structure.

AI was not used to write the project's implementation code. The design decisions, algorithms, architecture, and implementation were developed by the author.

Technical Choices

The project intentionally separates the different responsibilities of the application:

Parsing is separated from graph construction.
Graph representation is separated from pathfinding.
Path selection is separated from simulation.
Candidate distribution simulation is separated from the final drone execution.

This structure makes it possible to modify one stage without having to rewrite the entire application.

A particularly important design decision was to simulate candidate path distributions before moving the actual drones. This makes it possible to compare different routing strategies and choose the one that minimizes the total number of turns rather than simply choosing the individually shortest path for every drone.

The project therefore optimizes for overall simulation time, rather than only individual path cost.

*This project has been created as part of the 42 curriculum by ismonter.*

# Description

## Fly-in Drones

Fly-in Drones is a pathfinding and simulation project developed as part of the 42 curriculum.

The goal of the project is to move a given number of drones from a starting hub to an ending hub in the **fewest possible simulation turns**, while respecting the constraints imposed by the network.

The network is represented as a graph composed of hubs and connections:

- **Hubs** represent zones in the network.
- **Connections** represent links between hubs.
- **Drones** move through the network from the start hub to the end hub.
- Hubs can have different zone types and capacities.
- Connections can have a maximum number of drones that can use them simultaneously.

The project is divided into several main stages:

1. Parse and validate the input map.
2. Build an internal graph representation of the network.
3. Find all minimum-cost paths between the start and end hubs.
4. Find additional alternative paths with a cost of one or two turns above the minimum.
5. Generate different possible distributions of drones across these paths.
6. Simulate each distribution to determine how many turns it requires.
7. Select the distribution with the lowest number of turns.
8. Execute the selected strategy using the actual `Drone` objects.

The project also handles special movement rules such as restricted zones, which require two turns to reach, as well as hub and connection capacity limitations.

# Features

- Input file parsing and validation.
- Support for an arbitrary number of drones.
- Graph-based pathfinding.
- Multiple minimum-cost paths.
- Priority-zone preference when several paths have the same cost.
- Alternative paths with minimum cost +1 and minimum cost +2.
- Distribution of drones across multiple paths.
- Turn-by-turn simulation.
- Hub capacity management.
- Connection capacity management.
- Two-turn movement through restricted zones.
- Strategic waiting when movement is not possible.
- Prevention of path conflicts and capacity violations.
- Clear error messages for invalid configuration files.
- Terminal output showing drone movements.

# Algorithm

## Graph Representation

The network is represented as a graph.

Each `Hub` stores:

- Its name.
- Its coordinates.
- Its type (`start`, `end`, or regular hub).
- Its zone type (`normal`, `restricted`, `priority`, or `blocked`).
- Its maximum drone capacity.
- Its connections.

Each `Connection` stores:

- Its source hub.
- Its destination hub.
- Its maximum simultaneous capacity.

Connections are treated as bidirectional when navigating the graph.

## Pathfinding

The minimum-cost paths are calculated using a **Dijkstra-based algorithm**.

The cost of entering a hub depends on its zone type:

| Zone type | Movement cost |
|---|---:|
| `normal` | 1 |
| `priority` | 1 |
| `restricted` | 2 |
| `blocked` | Inaccessible |

Blocked hubs are excluded from navigation.

The pathfinding algorithm keeps track of both the minimum cost to reach every hub and the previous hubs that can produce that minimum cost.

This allows the program to reconstruct **all paths having the minimum cost**, rather than keeping only one path.

When multiple minimum-cost paths exist, they are ordered according to the number of `priority` hubs they contain. Paths containing more priority zones are preferred.

## Alternative Paths

Finding only the shortest paths is not always enough to obtain the fastest overall simulation.

Several drones may compete for the same hubs or connections, creating bottlenecks. Because of this, the project also searches for paths whose cost is:

- Minimum cost + 1.
- Minimum cost + 2.

These paths can sometimes provide a better overall distribution of drones even though an individual drone takes a slightly more expensive route.

The search is bounded to paths whose cost does not exceed `minimum_cost + 2`.

## Drone Distribution

After obtaining the minimum-cost paths and the alternative paths, the program creates several candidate distributions.

The basic distribution assigns drones cyclically across the available paths. For example, if there are three available paths:

```text
Drone 1 -> Path 1
Drone 2 -> Path 2
Drone 3 -> Path 3
Drone 4 -> Path 1
Drone 5 -> Path 2
...
