from map import Map
from drone import Drone
from hub import Hub


class Simulation():

    def __init__(self, map: Map) -> None:
        self.map = map
        self.current_turn = 1
        self.drones: list[Drone] = []
        self.assign_drones()

    def assign_drones(self):
        for index in range(1, self.map.nb_drones + 1):
            drone = Drone(index, self.map.get_start_hub())
            self.drones.append(drone)

    def count_hub_drones(self, hub: Hub) -> int:
        nbr_hub_drones = 0
        for drone in self.drones:
            if drone.current_hub == hub:
                nbr_hub_drones += 1
        return nbr_hub_drones

    def move_drone(self, id_drone: int, hub: Hub):
        nbr_hub_drones = self.count_hub_drones(hub)
        # if not hub.is_end():
        #   if nbr_hub_drones < hub.max_drones:
        #       self.drones[id_drone - 1].set_hub(hub)
