from hub import Hub
from connection import Connection

class Drone():
    """
    Represent a drone and its state during the simulation.
    A drone keeps track of its current hub, assigned path, movement
    progress, and whether it has reached the destination.
    """

    def __init__(self, drone_id: int, start_hub: Hub | None):
        """
        Initialize a drone.
        Args:
            drone_id: Unique identifier assigned to the drone.
            start_hub: Hub where the drone starts, if available.
        """
        self.id = drone_id
        self.current_hub: Hub | None = start_hub
        self.finished = False
        self.path = []
        self.path_index = 0
        self.connection: Connection | None = None

    def set_hub(self, hub: Hub) -> None:
        """
        Set the drone's current hub.
        Args:
            hub: Hub where the drone is currently located.
        """
        self.current_hub = hub

    def get_hub(self) -> Hub | None:
        """
        Return the drone's current hub.
        Returns:
            The hub where the drone is currently located, or None if
            no hub is assigned.
        """
        return self.current_hub

    def is_finished(self) -> bool:
        """
        Check whether the drone has reached its destination.
        Returns:
            True if the drone has finished its route, otherwise False.
        """
        return self.finished

    def finish(self) -> None:
        """Mark the drone as having reached its destination."""
        self.finished = True

    def set_path(self, path):
        """
        Assign a path to the drone and reset its path progress.
        Args:
            path: Sequence of hubs representing the drone's route.
        """
        self.path = path
        self.path_index = 0

    def __str__(self):
        """
        Return a human-readable representation of the drone.
        Returns:
            A string containing the drone identifier and current hub,
            or a message indicating that no hub is assigned.
        """
        if self.current_hub is None:
            return f"Drone {self.id}: no hub assigned"
        return f"Drone {self.id}: {self.current_hub.name}"
