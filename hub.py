from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from connection import Connection

class Hub():

    def __init__(self, name: str, x: int, y: int, hub_type: str, zone_type: str, color: str, max_drones: int):
        self.name = name
        self.x = x
        self.y = y
        self.hub_type = hub_type
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones
        self.connections: list["Connection"] = []


    def is_start(self) -> bool:
        if self.hub_type == "start":
            return True
        return False


    def is_end(self) -> bool:
        if self.hub_type == "end":
            return True
        return False


    def add_connection(self, connection: "Connection"):
        self.connections.append(connection)


    def get_connections(self) -> list["Connection"]:
        return self.connections

    def __str__(self) -> str:
        return f"Hub {self.name} ({self.x}, {self.y}) - {self.hub_type}"
