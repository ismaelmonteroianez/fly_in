from drone import Drone
from hub import Hub
from map import Map
from connection import Connection
from simulation import Simulation
from pathfinding import Pathfinding


class DroneController:

    def __init__(self, configuration: dict[str, object]) -> None:
        self.map = Map(configuration)
        self.pathfinding = Pathfinding(self.map)
        self.paths, self.minimum_cost = self.get_minimum_paths()
        self.alternative_paths = self.pathfinding.build_alternative_paths(self.minimum_cost)
        self.simulation = Simulation(self.map, self.paths, self.alternative_paths, self.minimum_cost)
        self.paths_assigned = self.simulation.assign_paths()
        self.current_turn = 1
        self.assign_paths_to_drones()

    def get_minimum_paths(self) -> tuple[list[list[Hub]], int]:
        previous, costs = self.pathfinding.find_path()
        paths = self.pathfinding.build_paths(previous)
        paths = self.pathfinding.reverse_paths(paths)
        paths.sort(key=self.pathfinding.count_priority_hubs,reverse=True)
        end_hub = self.map.get_end_hub()
        minimum_cost = costs[end_hub.name]
        return paths, minimum_cost

    def can_enter_hub(self, hub: Hub, hub_occupancy: int) -> bool:
        if hub.is_start() or hub.is_end():
            return True
        return hub.max_drones > hub_occupancy

    def can_enter_connection(self, connection: Connection, connection_occupancy: int) -> bool:
        return connection.get_max_link_capacity() > connection_occupancy

    def assign_paths_to_drones(self) -> None:
        for drone in self.simulation.drones:
            path = self.paths_assigned[drone.id - 1]
            drone.set_path(path)

    def all_drones_finished(self) -> bool:
        for drone in self.simulation.drones:
            if not drone.is_finished():
                return False
        return True

    def count_moves_from_hub(self,moves: list[Drone], hub: Hub) -> int:
        count = 0
        for drone in moves:
            if drone.get_hub() == hub:
                count += 1
        return count

    def process_transit_drones(self) -> set[int]:
        arrived_drones = set()
        for drone in self.simulation.drones:
            if drone.connection is None:
                continue
            next_hub = drone.path[drone.path_index + 1]
            drone.set_hub(next_hub)
            drone.connection = None
            drone.path_index += 1
            if next_hub.is_end():
                drone.finish()
            arrived_drones.add(drone.id)
        return arrived_drones

    def process_turn(self) -> None:
        arrived_drones = self.process_transit_drones()
        moves: list[Drone] = []
        hub_moves: dict[Hub, int] = {}
        connection_occupancy: dict[Connection, int] = {}
        for drone in self.simulation.drones:
            if drone.id in arrived_drones:
                continue
            current_hub = drone.get_hub()
            if current_hub is None:
                continue
            next_hub = drone.path[drone.path_index + 1]
            connection = current_hub.get_connection_to(next_hub)
            if connection is None:
                continue
            hub_drones = self.count_hub_drones(next_hub)
            connection_drones = connection_occupancy.get(connection, 0)
            hub_drones -= self.count_moves_from_hub(moves, next_hub)
            hub_drones += hub_moves.get(next_hub, 0)
            if next_hub.zone_type == "restricted":
                can_move = self.can_enter_connection(connection, connection_drones)
            else:
                can_move = (self.can_enter_hub(next_hub, hub_drones) and self.can_enter_connection( connection, connection_drones))


    def run(self) -> None:
        while not self.all_drones_finished():
            self.process_turn()
            self.current_turn += 1