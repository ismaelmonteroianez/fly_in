from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from connection import Connection


class Hub():
    """
    Represent a zone in the drone network.
    A hub stores its identification, coordinates, type, zone properties,
    drone capacity, and connections to other hubs.
    """

    def __init__(self, name: str, x: int, y: int, hub_type: str, zone_type: str, color: str, max_drones: int):
        """
        Initialize a hub with its network and zone properties.
        Args:
            name: Unique name of the hub.
            x: Horizontal coordinate of the hub.
            y: Vertical coordinate of the hub.
            hub_type: Type of hub, such as start, end, or regular.
            zone_type: Zone type defining its movement properties.
            color: Color associated with the hub for visualization.
            max_drones: Maximum number of drones allowed in the hub.
        """
        self.name = name
        self.x = x
        self.y = y
        self.hub_type = hub_type
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones
        self.connections: list["Connection"] = []

    def get_accessible_hubs(self) -> list["Hub"]:
        """
        Return the hubs that can be reached from this hub.
        Blocked hubs are excluded from the returned list.
        Returns:
            A list of accessible hubs connected to this hub.
        """
        accesible_hubs = []
        for connection in self.connections:
            hub_connected = connection.get_other_hub(self)
            if hub_connected is None:
                continue
            if hub_connected.zone_type == "blocked":
                continue
            accesible_hubs.append(hub_connected)
        return accesible_hubs

    def get_connection_to(self, hub: "Hub"):
        """
        Find the connection linking this hub to another hub.
        Args:
            hub: Hub to which the connection should lead.
        Returns:
            The connection to the specified hub, or None if no connection
            exists.
        """
        for connection in self.connections:
            if connection.get_other_hub(self) == hub:
                return connection
        return None

    def is_start(self) -> bool:
        """
        Check whether this hub is the starting hub.
        Returns:
            True if this is the start hub, otherwise False.
        """
        if self.hub_type == "start":
            return True
        return False

    def is_end(self) -> bool:
        """
        Check whether this hub is the destination hub.
        Returns:
            True if this is the end hub, otherwise False.
        """
        if self.hub_type == "end":
            return True
        return False

    def add_connection(self, connection: "Connection"):
        """
        Add a connection to this hub.
        Args:
            connection: Connection linking this hub to another hub.
        """
        self.connections.append(connection)

    def get_connections(self) -> list["Connection"]:
        """
        Return all connections associated with this hub.
        Returns:
            A list of connections linked to this hub.
        """
        return self.connections

    def __str__(self) -> str:
        """
        Return a human-readable representation of the hub.
        Returns:
            A string containing the hub name, coordinates, and type.
        """
        return f"Hub {self.name} ({self.x}, {self.y}) - {self.hub_type}"
