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
        print("SIMULATION OUTPUT:")
        print()
        positions = {}
        finished_drones = {}
        hub_occupancy = {}
        transit = {}
        for drone in self.drones:
            positions[drone.id] = 0
            finished_drones[drone.id] = False
            current_hub = paths_assigned[drone.id - 1][positions[drone.id]]
            transit[drone.id] = None
            if current_hub not in hub_occupancy:
                hub_occupancy[current_hub] = 0
            hub_occupancy[current_hub] += 1
        finished_count = 0
        turns = 0
        while finished_count < len(self.drones):
            moves = []
            output_moves = [] #eliminar despues
            turns += 1
            connection_occupancy = {}
            hub_moves = {}
            arrived_from_transit = set()
            for drone in self.drones:
                if transit[drone.id] is not None:
                    connection = transit[drone.id]
                    current_position = positions[drone.id]
                    next_hub = paths_assigned[drone.id - 1][current_position + 1]
                    #print(
                    #    "TRANSITO:",
                    #    "Dron:", drone.id,
                    #    "conexion:", connection,
                    #    "destino:", next_hub.name
                    #    )
                    positions[drone.id] += 1
                    transit[drone.id] = None
                    arrived_from_transit.add(drone.id)
                    output_moves.append(f"D{drone.id}-{next_hub.name}")
                    hub_occupancy[next_hub] = hub_occupancy.get(next_hub, 0) + 1
                    if positions[drone.id] == len(paths_assigned[drone.id - 1]) - 1:
                        finished_drones[drone.id] = True
                        finished_count += 1
            #print(
            #"POSICIONES:",
            #{drone.id: positions[drone.id] for drone in self.drones}
            #)
            #print(
            #"PATHS:",
            #[
            #[hub.name for hub in path]
            #for path in paths_assigned
            #]
            #)
            for drone in self.drones:
                if drone.id in arrived_from_transit:
                    continue
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
                #print(
                #    "TURNO:", turns,
                #    "Dron:", drone.id,
                #    "actual:", current_hub.name,
                #    "destino:", next_hub.name,
                #    "máx:", next_hub.max_drones,
                #    "ocupación:", hub_occupancy.get(next_hub, 0),
                #    "salidas:", self.count_moves_from_hub(
                #    moves, next_hub, paths_assigned, positions
                #    ),
                #    "entradas:", hub_moves.get(next_hub, 0),
                #   "total:", hub_drones
                #    )
                if next_hub.zone_type == "restricted":
                    can_move = self.can_enter_connection(connection, connection_drones)
                else:
                    can_move = (self.can_enter_hub(next_hub, hub_drones) and self.can_enter_connection(connection, connection_drones))
                if can_move:
                    moves.append(drone)
                    connection_occupancy[connection] = connection_occupancy.get(connection, 0) + 1
                    if next_hub.zone_type == "restricted":
                        transit[drone.id] = connection
                        connection_name = f"{connection.source.name}-{connection.destination.name}" #eliminar luego !!!!
                        output_moves.append(f"D{drone.id}-{connection_name}") #eliminar luego !!!
                    else:
                        hub_moves[next_hub] = hub_moves.get(next_hub, 0) + 1
                        output_moves.append(f"D{drone.id}-{next_hub.name}") #eliminar luego !!!
            #print("Turno:", turns, "Movimientos:", [drone.id for drone in moves])
            print(" ".join(output_moves))
            for drone in moves:
                current_hub = paths_assigned[drone.id - 1][positions[drone.id]]
                next_hub = paths_assigned[drone.id - 1][positions[drone.id] + 1]
                hub_occupancy[current_hub] -= 1
                if next_hub.zone_type == "restricted":
                    continue
                positions[drone.id] += 1
                if positions[drone.id] == len(paths_assigned[drone.id - 1]) - 1:
                    finished_drones[drone.id] = True
                    finished_count += 1
                hub_occupancy[next_hub] = hub_occupancy.get(next_hub, 0) + 1
        return turns

    def choose_best_distribution(self, distributions):
        best_distribution = distributions[0][0]
        best_turns = distributions[0][1]
        for distribution, turns in distributions:
            if turns < best_turns:
                best_distribution = distribution
                best_turns = turns
        return best_distribution

    def build_distribution(self, paths):
        distribution = []
        number_of_paths = len(paths)
        for drone_index in range(len(self.drones)):
            path = paths[drone_index % number_of_paths]
            distribution.append(path)
        return distribution

    def build_minimum_distribution(self):
        return self.build_distribution(self.paths)

    def assign_paths(self):
        if not self.paths:
            return []
        paths_plus_one = []
        paths_plus_two = []
        for path, cost in self.alternative_paths:
            if cost == self.minimum_cost + 1:
                paths_plus_one.append(path)
            elif cost == self.minimum_cost + 2:
                paths_plus_two.append(path)
        minimum_distribution = self.build_minimum_distribution()
        turns_minimum = self.calculate_turns(minimum_distribution)
        plus_one_distribution = None
        turns_plus_one = None
        plus_two_distribution = None
        turns_plus_two = None
        plus_one_two_distribution = None
        turns_plus_one_two = None
        if paths_plus_one:
            available_paths = self.paths + paths_plus_one
            plus_one_distribution = self.build_distribution(available_paths)
            turns_plus_one = self.calculate_turns(plus_one_distribution)
        if len(paths_plus_one) >= 2:
            available_paths = self.paths + paths_plus_one[:2]
            plus_one_two_distribution = self.build_distribution(available_paths)
            turns_plus_one_two = self.calculate_turns(plus_one_two_distribution)
        if paths_plus_two:
            available_paths = self.paths + paths_plus_two
            plus_two_distribution = self.build_distribution(available_paths)
            turns_plus_two = self.calculate_turns(plus_two_distribution)
        print("\n")
        print("Distribución mínima:")
        print([[hub.name for hub in path] for path in minimum_distribution])
        print("Turns:", turns_minimum)
        print("\n")
        if plus_one_distribution is not None:
            print("Distribución mínima + caminos +1:")
            print([[hub.name for hub in path]for path in plus_one_distribution])
            print("Turns:", turns_plus_one)
        if plus_one_two_distribution is not None:
            print("\n")
            print("Distribución mínima + 2 caminos +1:")
            print([[hub.name for hub in path] for path in plus_one_two_distribution])
            print("Turns:", turns_plus_one_two)
        if plus_two_distribution is not None:
            print("\n")
            print("Distribución mínima + caminos +2:")
            print([[hub.name for hub in path] for path in plus_two_distribution])
            print("Turns:", turns_plus_two)
        distributions = [(minimum_distribution, turns_minimum)]
        if plus_one_distribution is not None:
            distributions.append((plus_one_distribution, turns_plus_one))
        if plus_two_distribution is not None:
            distributions.append((plus_two_distribution, turns_plus_two))
        if plus_one_two_distribution is not None:
            distributions.append((plus_one_two_distribution, turns_plus_one_two))
        return self.choose_best_distribution(distributions)

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
