from map import Map
from hub import Hub


class Pathfinding():

    def __init__(self, map: Map):
        self.map = map

    def reverse_paths(self, inverted_paths):
        paths = []
        for path in inverted_paths:
            path.reverse()
            paths.append(path)
        return paths

    def count_priority_hubs(self, path: list[Hub]) -> int:
        priority_count = 0
        for hub in path:
            if hub.zone_type == "priority":
                priority_count += 1
        return priority_count

    def build_alternative_paths(self, minimum_cost):
        alternative_paths = []
        pending = []
        current = self.map.get_start_hub()
        pending.append(([current], 0))
        while pending:
            path, current_cost = pending.pop()
            if path[-1] == self.map.get_end_hub():
                if minimum_cost < current_cost <= minimum_cost + 2:
                    alternative_paths.append((path, current_cost))
                continue
            current = path[-1]
            neighbours = current.get_accessible_hubs()
            for neighbour in neighbours:
                step_cost = 0
                if neighbour in path:
                    continue
                if neighbour.zone_type == "normal" or neighbour.zone_type == "priority":
                    step_cost = 1
                elif neighbour.zone_type == "restricted":
                    step_cost = 2
                new_cost = current_cost + step_cost
                if new_cost > minimum_cost + 2:
                    continue
                new_path = path[:]
                new_path.append(neighbour)
                pending.append((new_path, new_cost))
        return alternative_paths


    def build_paths(self, previous):
        paths = []
        pending = []
        current = self.map.get_end_hub()
        pending.append([current])
        while pending:
            path = pending.pop()
            if path[-1] == self.map.get_start_hub():
                paths.append(path)
                continue
            current = path[-1]
            previous_hubs = previous[current.name]
            if len(previous_hubs) == 1:
                path.append(previous_hubs[0])
                pending.append(path)
            if len(previous_hubs) > 1:
                for previous_hub in previous_hubs:
                    new_path = path[:]
                    new_path.append(previous_hub)
                    pending.append(new_path)
        return paths


    def find_path(self):
        costs = {}
        previous = {}
        pending: list[Hub] = []
        for hub in self.map.hubs.values():
            if hub == self.map.get_start_hub():
                costs[hub.name] = 0
            else:
                costs[hub.name] = float("inf")
            previous[hub.name] = []
            pending.append(hub)
        while pending != []:
            min_cost = float("inf")
            current: None | Hub = None
            for hub in pending:
                if min_cost > costs[hub.name]:
                    min_cost = costs[hub.name]
                    current = hub
            if current is None:
                break
            for neighbour in current.get_accessible_hubs():
                new_cost = costs[current.name]
                if neighbour.zone_type == "normal" or neighbour.zone_type == "priority":
                    new_cost += 1
                elif neighbour.zone_type == "restricted":
                    new_cost += 2
                if new_cost < costs[neighbour.name]:
                    costs[neighbour.name] = new_cost
                    previous[neighbour.name] = [current]
                elif new_cost == costs[neighbour.name]:
                    previous[neighbour.name].append(current)
            pending.remove(current)
        return previous, costs
