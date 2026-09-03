from hub import Hub
from connection import Connection


class Map():
    """
    Represent the drone network map.
    A map contains all hubs and connections defined in the configuration
    and establishes the relationships between connected hubs.
    """
    def __init__(self, configuration):
        """
        Initialize the map from a parsed configuration.
        Args:
            configuration: Dictionary containing the number of drones,
                hub definitions, and connection definitions.
        """
        self.configuration: dict[str, object] = configuration
        self.nb_drones = configuration["nb_drones"]
        self.hubs: dict[str, Hub] = {}
        self.connections: list[Connection] = []
        self.create_hubs(configuration["hubs"])
        self.create_connections(configuration["connections"])
        self.add_connections_to_hubs()

    def create_hubs(self, hubs_data):
        """
        Create and store all hubs defined in the configuration.
        Args:
            hubs_data: Dictionary containing the configuration data
                for each hub.
        """
        for hub_name, hub_data in hubs_data.items():
            metadata = hub_data["metadata"]
            hub = Hub(hub_name, hub_data["x"], hub_data["y"], hub_data["type"], metadata["zone"], metadata["color"], metadata["max_drones"])
            self.hubs[hub_name] = hub

    def create_connections(self, connections_data):
        """
        Create and store all connections defined in the configuration.
        Args:
            connections_data: List containing the configuration data
                for each connection.
        """
        for connection_data in connections_data:
            source = self.hubs[connection_data["zone1"]]
            destination = self.hubs[connection_data["zone2"]]
            connection = Connection(source, destination, connection_data["max_link_capacity"])
            self.connections.append(connection)

    def add_connections_to_hubs(self):
        """
        Add each connection to both hubs that it links.
        """
        for connection in self.connections:
            connection.source.add_connection(connection)
            connection.destination.add_connection(connection)

    def get_hub(self, name: str) -> Hub:
        """
        Return a hub by its name.
        Args:
            name: Name of the hub to retrieve.
        Returns:
            The hub with the specified name.
        """
        return self.hubs[name]

    def get_start_hub(self) -> Hub | None:
        """
        Find and return the starting hub of the map.
        Returns:
            The start hub if one is found, otherwise None.
        """
        for hub in self.hubs.values():
            if hub.is_start():
                return hub

    def get_end_hub(self) -> Hub | None:
        """
        Find and return the destination hub of the map.
        Returns:
            The end hub if one is found, otherwise None.
        """
        for hub in self.hubs.values():
            if hub.is_end():
                return hub
