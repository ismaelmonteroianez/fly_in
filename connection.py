from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from hub import Hub


class Connection():
    """
    Represent a bidirectional connection between two hubs.
    A connection stores its source and destination hubs and the maximum
    number of drones that can traverse it simultaneously.
    """


    def __init__(self, source: "Hub", destination: "Hub", max_link_capacity: int):
        """
        Initialize a connection between two hubs.
        Args:
            source: Hub where the connection starts.
            destination: Hub where the connection ends.
            max_link_capacity: Maximum number of drones that can use
                the connection simultaneously.
        """
        self.source = source
        self.destination = destination
        self.max_link_capacity = max_link_capacity

    def get_source(self) -> "Hub":
        """
        Return the source hub of the connection.
        Returns:
            The hub where the connection starts.
        """
        return self.source

    def get_destination(self) -> "Hub":
        """
        Return the destination hub of the connection.
        Returns:
            The hub where the connection ends.
        """
        return self.destination

    def get_other_hub(self, hub: "Hub") -> "Hub | None":
        """
        Return the hub connected to the given hub.
        Args:
            hub: Hub from which to find the connected hub.
        Returns:
            The other hub connected by this connection, or None if the
            given hub is not part of the connection.
        """
        if hub == self.source:
            return self.destination
        elif hub == self.destination:
            return self.source
        else:
            return None

    def get_max_link_capacity(self) -> int:
        """
        Return the maximum capacity of the connection.
        Returns:
            The maximum number of drones allowed on the connection
            simultaneously.
        """
        return self.max_link_capacity

    def __str__(self) -> str:
        """
        Return a human-readable representation of the connection.
        Returns:
            A string containing the connected hubs and their capacity.
        """
        return f"Connection {self.source.name} -> {self.destination.name} - capacity: {self.max_link_capacity}"
