from hub import Hub
from connection import Connection

class Drone():

    def __init__(self, drone_id: int, start_hub: Hub | None):
        self.id = drone_id
        self.current_hub: Hub | None = start_hub
        self.finished = False
        self.path = []
        self.path_index = 0
        self.connection: Connection | None = None

    def set_hub(self, hub: Hub) -> None:
        self.current_hub = hub

    def get_hub(self) -> Hub | None:
        return self.current_hub

    def is_finished(self) -> bool:
        return self.finished

    def finish(self) -> None:
        self.finished = True

    def set_path(self, path):
        self.path = path
        self.path_index = 0

    def __str__(self):
        if self.current_hub is None:
            return f"Drone {self.id}: no hub assigned"
        return f"Drone {self.id}: {self.current_hub.name}"
