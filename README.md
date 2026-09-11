*This project has been created as part of the 42 curriculum by ismonter.*

# Fly-in

> An object-oriented drone-routing simulator written in Python.

Fly-in moves a fleet of drones from a start hub to an end hub through a connected network of zones. It calculates routes, distributes drones across them, and simulates every turn while respecting movement costs and capacity limits.

## Description

The goal is to deliver every drone in the fewest possible simulation turns. The program reads a text map, validates its hubs and connections, creates a bidirectional graph, finds efficient routes, evaluates candidate drone distributions, and displays the final turn-by-turn simulation. It implements the graph logic directly and uses no graph library.

## Contents

- [Instructions](#instructions)
- [Map format](#map-format)
- [Example input and expected output](#example-input-and-expected-output)
- [How it works](#how-it-works)
- [Visual output](#visual-output)
- [Project structure](#project-structure)
- [Resources](#resources)

## Instructions

### Requirements

| Tool | Purpose |
| --- | --- |
| Python 3.10+ | Run the simulator |
| `flake8` | Style checking (development) |
| `mypy` | Static type checking (development) |

Install the development tools:

```sh
make install
```

Run one of the included maps:

```sh
python3 fly_in.py maps/easy/01_linear_path.txt
```

The Makefile also provides these commands:

```sh
make run MAP=maps/easy/01_linear_path.txt
make debug MAP=maps/easy/01_linear_path.txt
make lint
make clean
```

The program expects exactly one existing file with a `.txt` extension. More maps are available in [`maps/`](maps/README.md).

## Map format

Blank lines and comments beginning with `#` are ignored. The first meaningful line defines a positive number of drones. A map must contain exactly one start hub and one end hub.

### Hubs

```text
start_hub: <name> <x> <y> [metadata]
end_hub:   <name> <x> <y> [metadata]
hub:       <name> <x> <y> [metadata]
```

Hub metadata is optional and accepts the following keys:

| Key | Default | Meaning |
| --- | --- | --- |
| `zone` | `normal` | Zone movement rule |
| `color` | `none` | ANSI output colour |
| `max_drones` | `1` | Maximum simultaneous drones in the hub |

Names cannot contain `-`; coordinates must be integers. Supported colours are `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`, `orange`, `purple`, `brown`, `lime`, `gold`, `maroon`, `darkred`, `violet`, `crimson`, and `rainbow`.

### Connections

```text
connection: <hub1>-<hub2> [max_link_capacity=<positive integer>]
```

Connections are bidirectional. Their default capacity is `1`, and both endpoint hubs must have been declared earlier in the file.

### Zone rules

| Zone | Cost to enter | Effect |
| --- | ---: | --- |
| `normal` | 1 turn | Standard accessible hub. |
| `priority` | 1 turn | Preferred when otherwise equal-cost routes are available. |
| `restricted` | 2 turns | The drone spends one turn in transit, then arrives on the next turn. |
| `blocked` | — | Cannot be used by pathfinding or entered by a drone. |

The start and end hubs have unlimited occupancy. All other hubs follow `max_drones`.

## Example input and expected output

### Example input

The supplied file `maps/easy/01_linear_path.txt` contains:

```text
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

Run it with:

```sh
python3 fly_in.py maps/easy/01_linear_path.txt
```

### Expected output

The output below was produced by the implementation. ANSI escape codes are removed only to keep this README readable:

```text
REAL OUTPUT:

D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal
```

Each output line represents one simulation turn. `D1-waypoint1` means drone 1 entered `waypoint1`. A movement into a restricted hub is initially printed as `D<id>-<source>-<destination>` because the drone is in transit; its arrival is printed on the following turn.

## How it works

### 1. Parse and build the network

`parser.py` validates the map and reports invalid configuration data clearly. `Map`, `Hub`, and `Connection` turn the parsed data into a bidirectional graph.

### 2. Find routes

`Pathfinding` uses Dijkstra's algorithm with the cost of entering each zone. Blocked hubs are skipped. It keeps every predecessor that produces the same minimum cost, so it can reconstruct all shortest routes—not just one.

When shortest routes have equal cost, routes containing more `priority` hubs are ordered first. The program also explores loop-free alternatives costing at most two turns more than the optimum.

### 3. Select a distribution

`Simulation` assigns drones round-robin over available routes and simulates candidate distributions before the real run. It compares the shortest-route distribution with applicable `+1`, `+2`, and combined `+1` alternatives, then keeps the distribution requiring the fewest turns. For fleets larger than 1,000 drones, it uses only shortest routes to limit this extra work.

### 4. Simulate turns

`DroneController` executes the selected distribution. At every turn it:

1. Completes drones already travelling through restricted zones.
2. Checks destination occupancy and link capacity.
3. Reserves all valid moves.
4. Executes the approved moves together.
5. Leaves drones in place when a move cannot be made.

The shortest-path search selects its next pending hub with a linear scan, giving it an approximate complexity of **O(V² + E)**. The cost of reconstructing routes and evaluating distributions depends on the number of valid paths; alternative-route exploration is bounded to two additional cost units and prevents cycles.

## Visual output

The terminal output is also the project's visual representation. Each movement is rendered with the ANSI colour configured for its destination hub, making simultaneous movements easier to distinguish. `rainbow` is supported as a special multi-colour option. If ANSI colours are not displayed by the terminal, the movement tokens remain fully readable.

## Project structure

```text
.
├── fly_in.py             Command-line entry point
├── parser.py             Input parsing and validation
├── map.py                Graph construction
├── hub.py                Hub model and adjacency access
├── connection.py         Bidirectional connection model
├── pathfinding.py        Shortest and alternative route discovery
├── simulation.py         Candidate-distribution evaluation
├── drone_controller.py   Turn execution and output
├── drone.py              Drone state model
├── terminal_color.py     ANSI colour rendering
└── maps/                 Example maps by difficulty
```

## Resources

- [Dijkstra's algorithm — CP-Algorithms](https://cp-algorithms.com/graph/dijkstra.html)
- [Python type hints](https://docs.python.org/3/library/typing.html)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [ANSI escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code)

### AI usage

AI was used to review the subject and the existing implementation, and to help reviewing this README. No application source code or routing algorithm was generated or modified by AI.
