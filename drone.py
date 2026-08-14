class Drone():

    def __init__(self, drone_id: int):
        self.id = drone_id
        self.current_hub = None
        self.finished = False


    def set_hub(self, hub) -> None:
        self.current_hub = hub


    def get_hub(self):
        return self.current_hub


    def is_finished(self) -> bool:
        return self.finished


    def finish(self) -> None:
        self.finished = True


    def __str__(self):
        if self.current_hub is None:
            return f"Drone {self.id}: no hub assigned"
        return f"Drone {self.id}: {self.current_hub.name}"
    
