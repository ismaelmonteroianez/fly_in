from hub import Hub


class Drone():

    def __init__(self, drone_id: int, start_hub: Hub | None):
        self.id = drone_id
        self.current_hub: Hub | None = start_hub
        self.finished = False


    def set_hub(self, hub: Hub) -> None:
        self.current_hub = hub


    def get_hub(self) -> Hub | None:
        return self.current_hub


    def is_finished(self) -> bool:
        return self.finished


    def finish(self) -> None:
        self.finished = True


    def __str__(self):
        if self.current_hub is None:
            return f"Drone {self.id}: no hub assigned"
        return f"Drone {self.id}: {self.current_hub.name}"
    
