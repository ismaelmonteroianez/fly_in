from map import Map
from hub import Hub


class Pathfinding():

    def __init__(self, map: Map):
        self.map = map

    def find_path(self):
        costs = {}
        previous = {}
        pending: list[Hub] = []
        for hub in self.map.hubs.values():
            if hub == self.map.get_start_hub():
                costs[hub.name] = 0
            else:
                costs[hub.name] = float("inf")
            previous[hub.name] = None
            pending.append(hub)
        while pending != []:
            min_cost = float("inf")
            current: None | Hub = None
            for hub in pending:
                if min_cost > costs[hub.name]:
                    min_cost = costs[hub.name]
                    current = hub
            if current is not None:
                for neighbour in current.get_accessible_hubs():
                    new_cost = costs[current.name]
                    if neighbour.zone_type == "normal" or neighbour.zone_type == "priority":
                        new_cost += 1
                    elif neighbour.zone_type == "restricted":
                        new_cost += 2
                    if new_cost < costs[neighbour.name]:
                        costs[neighbour.name] = new_cost
                        previous[neighbour.name] = current
                pending.remove(current)
        path = []
        current =  self.map.get_end_hub()
        while current is not None:
            path.append(current)
            current = previous[current.name]
        path.reverse()
        return path