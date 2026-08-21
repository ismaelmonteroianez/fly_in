from map import Map
from drone import Drone
from hub import Hub
from connection import Connection

class Simulation():

    def __init__(self, map: Map, paths, alternative_paths, minimum_cost) -> None:
        self.map = map
        self.current_turn = 1
        self.drones: list[Drone] = []
        self.paths = paths
        self.alternative_paths = alternative_paths
        self.minimum_cost = minimum_cost
        self.assign_drones()
        self.paths_assigned = self.assign_paths()

    def can_enter_connection(self, connection: Connection, connection_occupancy: int) -> bool:
        if connection.get_max_link_capacity() > connection_occupancy:
            return True
        return False

    def can_enter_hub(self, hub: Hub, hub_occupancy: int) -> bool:
        if hub.is_start() or hub.is_end():
            return True
        if hub.max_drones > hub_occupancy:
            return True
        return False

    def count_moves_from_hub(self, moves, hub, paths_assigned, positions):
        count = 0
        for drone in moves:
            current_hub = paths_assigned[drone.id - 1][positions[drone.id]]
            if current_hub == hub:
                count += 1
        return count

    def calculate_turns(self, paths_assigned) -> int:
        #positions[drone_id]     → índice
        #assignment[drone_id-1]  → camino
        #assignment[drone_id-1][positions[drone_id]] → hub actual

        positions = {}
        finished_drones = {}
        hub_occupancy = {}
        transit = {}
        for drone in self.drones:
            positions[drone.id] = 0
            finished_drones[drone.id] = False
            current_hub = paths_assigned[drone.id - 1][positions[drone.id]]
            transit[drone.id] = 0
            if current_hub not in hub_occupancy:
                hub_occupancy[current_hub] = 0
            hub_occupancy[current_hub] += 1
        finished_count = 0
        turns = 0
        while finished_count < len(self.drones):
            moves = []
            turns += 1
            connection_occupancy = {}
            hub_moves = {}
            print(
            "POSICIONES:",
            {drone.id: positions[drone.id] for drone in self.drones}
            )
            print(
            "PATHS:",
            [
            [hub.name for hub in path]
            for path in paths_assigned
            ]
            )
            for drone in self.drones:
                current_hub: Hub = paths_assigned[drone.id - 1][positions[drone.id]]
                if positions[drone.id] == len(paths_assigned[drone.id - 1]) - 1:
                    if finished_drones[drone.id]:
                        continue
                next_hub = paths_assigned[drone.id - 1][positions[drone.id] + 1]
                connection = current_hub.get_connection_to(next_hub)
                hub_drones = hub_occupancy.get(next_hub, 0)
                connection_drones = connection_occupancy.get(connection, 0)
                hub_drones -= self.count_moves_from_hub(moves, next_hub, paths_assigned, positions)
                hub_drones += hub_moves.get(next_hub, 0)
                print(
                    "Dron:", drone.id,
                    "destino:", next_hub.name,
                    "máx:", next_hub.max_drones,
                    "ocupación:", hub_occupancy.get(next_hub, 0),
                    "salidas:", self.count_moves_from_hub(
                    moves, next_hub, paths_assigned, positions
                    ),
                    "entradas:", hub_moves.get(next_hub, 0),
                    "total:", hub_drones
                    )
                if self.can_enter_hub(next_hub, hub_drones) and self.can_enter_connection(connection, connection_drones):
                    moves.append(drone)
                    connection_occupancy[connection] = connection_occupancy.get(connection, 0) + 1
                    hub_moves[next_hub] = hub_moves.get(next_hub, 0) + 1
            print("Turno:", turns, "Movimientos:", [drone.id for drone in moves])
            for drone in moves:
                current_hub = paths_assigned[drone.id - 1][positions[drone.id]]
                next_hub = paths_assigned[drone.id - 1][positions[drone.id] + 1]
                positions[drone.id] += 1
                if positions[drone.id] == len(paths_assigned[drone.id - 1]) - 1:
                    finished_drones[drone.id] = True
                    finished_count += 1
                hub_occupancy[current_hub] -= 1
                hub_occupancy[next_hub] = hub_occupancy.get(next_hub, 0) + 1
        return turns

    def assign_paths(self):
        paths_assigned = []
        if not self.paths:
            return []
        number_of_paths = len(self.paths)
        number_of_drones = len(self.drones)
        path_plus_one = None
        for path, cost in self.alternative_paths:
            if cost == self.minimum_cost + 1:
                path_plus_one = path
                break
        print("\n")
        print(
            "PATH +1:",
            [hub.name for hub in path_plus_one]
            if path_plus_one else None
        )
        for drone_index in range(number_of_drones):
            path = self.paths[drone_index % number_of_paths]
            paths_assigned.append(path)

        turns = self.calculate_turns(paths_assigned)
        print("\n")
        print("Asignación:", [
            [hub.name for hub in path]
            for path in paths_assigned
            ])
        print("Turns:", turns)
        return paths_assigned

    def assign_drones(self):
        for index in range(1, self.map.nb_drones + 1):
            drone = Drone(index, self.map.get_start_hub())
            self.drones.append(drone)

    def count_connection_drones(self, connection: Connection) -> int:
        nbr_connection_drones = 0
        for drone in self.drones:
            if drone.connection == connection:
                nbr_connection_drones += 1
        return nbr_connection_drones

    def count_hub_drones(self, hub: Hub) -> int:
        nbr_hub_drones = 0
        for drone in self.drones:
            if drone.current_hub == hub:
                nbr_hub_drones += 1
        return nbr_hub_drones

    def assign_path_to_drone(self, drone, path):
        drone.set_path(path)

    def move_drone(self, id_drone: int, hub: Hub):
        nbr_hub_drones = self.count_hub_drones(hub)
        # if not hub.is_end():
        #   if nbr_hub_drones < hub.max_drones:
        #       self.drones[id_drone - 1].set_hub(hub)
