from hub import Hub
from connection import Connection


class Map():

    def __init__(self, configuration):
        self.configuration : dict[str, object] = configuration
        self.nb_drones = configuration["nb_drones"]
        self.hubs : dict[str, Hub] = {}
        self.connections : list[Connection] = []
        self.create_hubs(configuration["hubs"])
        self.create_connections(configuration["connections"])
        self.add_connections_to_hubs()


    def create_hubs(self, hubs_data):
        for hub_name, hub_data in hubs_data.items():
            metadata = hub_data["metadata"]
            hub = Hub(hub_name, hub_data["x"], hub_data["y"], hub_data["type"], metadata["zone"], metadata["color"], metadata["max_drones"])
            self.hubs[hub_name] = hub


    def create_connections(self, connections_data):
        for connection_data in connections_data:
            source = self.hubs[connection_data["zone1"]]
            destination = self.hubs[connection_data["zone2"]]
            connection = Connection(source, destination, connection_data["max_link_capacity"])
            self.connections.append(connection)


    def add_connections_to_hubs(self):
        for connection in self.connections:
            connection.source.add_connection(connection)
            connection.destination.add_connection(connection)


    def get_hub(self, name: str) -> Hub:
        return self.hubs[name]


    def get_start_hub(self) -> Hub | None:
        for hub in self.hubs.values():
            if hub.is_start():
                return hub    


    def get_end_hub(self) -> Hub | None:
        for hub in self.hubs.values():
            if hub.is_end():
                return hub
