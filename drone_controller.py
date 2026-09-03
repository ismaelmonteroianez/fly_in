from drone import Drone
from hub import Hub
from map import Map
from connection import Connection
from simulation import Simulation
from pathfinding import Pathfinding


class DroneController:
    """
    Coordinate pathfinding, path assignment, and drone simulation.
    The controller builds the map from the parsed configuration, calculates
    the available paths, selects the best path distribution, assigns paths
    to the drones, and executes the simulation turn by turn.
    """

    def __init__(self, configuration: dict[str, object]) -> None:
        """
        Initialize the drone controller with the provided configuration.
        Args:
            configuration: Parsed configuration containing the number of
                drones, hubs, and connections.
        """
        self.map = Map(configuration)
        self.pathfinding = Pathfinding(self.map)
        self.paths, self.minimum_cost = self.get_minimum_paths()
        self.alternative_paths = self.pathfinding.build_alternative_paths(self.minimum_cost)
        self.simulation = Simulation(self.map, self.paths, self.alternative_paths, self.minimum_cost)
        self.paths_assigned = self.simulation.assign_paths()
        self.current_turn = 1
        self.assign_paths_to_drones()

    def get_minimum_paths(self) -> tuple[list[list[Hub]], int]:
        """
        Find all paths with the minimum movement cost.
        Paths with the same minimum cost are ordered by the number of
        priority hubs they contain, giving preference to paths with more
        priority zones.
        Returns:
            A tuple containing the list of minimum-cost paths and their
            common minimum cost.
        """
        previous, costs = self.pathfinding.find_path()
        paths = self.pathfinding.build_paths(previous)
        paths = self.pathfinding.reverse_paths(paths)
        paths.sort(key=self.pathfinding.count_priority_hubs,reverse=True)
        end_hub = self.map.get_end_hub()
        minimum_cost = costs[end_hub.name]
        return paths, minimum_cost

    def can_enter_hub(self, hub: Hub, hub_occupancy: int) -> bool:
        """
        Check whether a drone can enter a hub.
        The start and end hubs have no occupancy limit. Other hubs can only
        accept a drone if their maximum capacity is not exceeded.
        Args:
            hub: Hub that the drone wants to enter.
            hub_occupancy: Current or projected number of drones in the hub.
        Returns:
            True if the hub can accept the drone, otherwise False.
        """
        if hub.is_start() or hub.is_end():
            return True
        return hub.max_drones > hub_occupancy

    def can_enter_connection(self, connection: Connection, connection_occupancy: int) -> bool:
        """
        Check whether a drone can enter a connection.
        Args:
            connection: Connection that the drone wants to use.
            connection_occupancy: Number of drones already using the
                connection during the current turn.
        Returns:
            True if the connection has available capacity, otherwise False.
        """
        return connection.get_max_link_capacity() > connection_occupancy

    def assign_paths_to_drones(self) -> None:
        """
        Assign the selected path to each drone.
        Each drone receives the path corresponding to its identifier in the
        selected path distribution.
        """
        for drone in self.simulation.drones:
            path = self.paths_assigned[drone.id - 1]
            drone.set_path(path)

    def all_drones_finished(self) -> bool:
        """
        Check whether all drones have reached the destination.
        Returns:
            True if every drone has finished the simulation, otherwise False.
        """
        for drone in self.simulation.drones:
            if not drone.is_finished():
                return False
        return True

    def count_moves_from_hub(self,moves: list[Drone], hub: Hub) -> int:
        """
        Count pending drone movements originating from a specific hub.
        Args:
            moves: Drones scheduled to move during the current turn.
            hub: Hub whose outgoing movements should be counted.
        Returns:
            The number of scheduled movements originating from the hub.
        """
        count = 0
        for drone in moves:
            if drone.get_hub() == hub:
                count += 1
        return count

    def get_move_output(self, drone: Drone, next_hub: Hub, connection: Connection) -> str:
        """
        Generate the output representation of a drone movement.
        Restricted-zone movements are represented by the connection used,
        while regular movements are represented by the destination hub.
        Args:
            drone: Drone performing the movement.
            next_hub: Destination hub of the movement.
            connection: Connection used by the drone.

        Returns:
            A formatted string describing the drone movement.
        """
        if next_hub.zone_type == "restricted":
            return f"D{drone.id}-{connection.source.name}-{connection.destination.name}"
        return f"D{drone.id}-{next_hub.name}"

    def process_transit_drones(self) -> tuple[set[int], list[str]]:
        """
        Process drones completing a two-turn restricted-zone movement.
        Drones currently in transit are moved to their destination hub,
        removed from their connection, and marked as finished if they reach
        the end hub.
        Returns:
            A tuple containing the identifiers of drones that arrived and
            the formatted movement output for those drones.
        """
        arrived_drones = set()
        output_moves: list[str] = []
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
            output_moves.append(f"D{drone.id}-{next_hub.name}")
        return arrived_drones, output_moves

    def register_move(self, drone: Drone, next_hub: Hub,
    connection: Connection, moves: list[Drone], hub_moves: dict[Hub, int],
    connection_occupancy: dict[Connection, int]) -> None:
        """
        Register a valid drone movement for the current turn.
        The movement is added to the pending movements and the connection
        occupancy is updated. Restricted-zone movements place the drone in
        transit, while regular movements reserve capacity in the destination
        hub.
        Args:
            drone: Drone that will perform the movement.
            next_hub: Destination hub.
            connection: Connection used by the drone.
            moves: List of movements scheduled during the current turn.
            hub_moves: Number of pending movements into each destination hub.
            connection_occupancy: Number of drones using each connection
                during the current turn.
        """
        moves.append(drone)
        connection_occupancy[connection] = (connection_occupancy.get(connection, 0) + 1)
        if next_hub.zone_type == "restricted":
            drone.connection = connection
        else:
            hub_moves[next_hub] = hub_moves.get(next_hub, 0) + 1

    def execute_moves(self, moves: list[Drone]) -> None:
        """
        Apply all valid non-transit drone movements.
        Drones entering restricted zones remain in transit and are not moved
        to their destination hub until the following turn.
        Args:
            moves: Drones scheduled to move during the current turn.
        """
        for drone in moves:
            current_hub = drone.get_hub()
            next_hub = drone.path[drone.path_index + 1]
            if current_hub is None:
                continue
            if next_hub.zone_type == "restricted":
                continue
            drone.set_hub(next_hub)
            drone.path_index += 1
            if next_hub.is_end():
                drone.finish()

    def process_turn(self) -> None:
        """
        Process one complete simulation turn.
        Transit drones are processed first. The controller then evaluates
        each remaining drone, checks hub and connection capacities, registers
        valid movements, executes them, and outputs the movements performed
        during the turn.
        """
        arrived_drones, output_moves = self.process_transit_drones()
        moves: list[Drone] = []
        hub_moves: dict[Hub, int] = {}
        connection_occupancy: dict[Connection, int] = {}
        for drone in self.simulation.drones:
            if drone.id in arrived_drones:
                continue
            current_hub = drone.get_hub()
            if current_hub is None:
                continue
            if drone.is_finished(): 
                continue
            next_hub = drone.path[drone.path_index + 1]
            connection = current_hub.get_connection_to(next_hub)
            if connection is None:
                continue
            hub_drones = self.simulation.count_hub_drones(next_hub)
            connection_drones = connection_occupancy.get(connection, 0)
            hub_drones -= self.count_moves_from_hub(moves, next_hub)
            hub_drones += hub_moves.get(next_hub, 0)
            if next_hub.zone_type == "restricted":
                can_move = self.can_enter_connection(connection, connection_drones)
            else:
                can_move = (self.can_enter_hub(next_hub, hub_drones) and self.can_enter_connection( connection, connection_drones))
            if can_move: 
                self.register_move(drone, next_hub,connection, moves, hub_moves, connection_occupancy)
                output_moves.append(self.get_move_output(drone, next_hub, connection))
        self.execute_moves(moves)
        print(" ".join(output_moves))

    def run(self) -> None:
        """
        Run the simulation until all drones reach the end hub.
        Each simulation turn is processed sequentially until every drone
        has been marked as finished.
        """
        print("REAL OUTPUT:")
        print()
        while not self.all_drones_finished():
            self.process_turn()
            self.current_turn += 1