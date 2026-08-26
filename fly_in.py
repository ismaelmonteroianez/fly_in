from parser import parser, EmptyFile, InvalidConfiguration
import sys
import os
from simulation import Simulation
from map import Map
from pathfinding import Pathfinding

def main() -> None:
    if len(sys.argv) == 2:
        file_path = sys.argv[1]
        if not file_path.lower().endswith(".txt"):
            print("Invalid file type: expected a .txt file")
            return
        if not os.path.isfile(file_path):
            print(f"No such file or directory: {file_path}")
            return
        try:
            configuration = parser(file_path)
            #print(configuration)
            map = Map(configuration)
            pathfinding = Pathfinding(map)
            previous, costs = pathfinding.find_path()
            paths = pathfinding.build_paths(previous)
            paths = pathfinding.reverse_paths(paths)
            paths.sort(key=pathfinding.count_priority_hubs, reverse=True)
            minimum_cost = costs[map.get_end_hub().name]
            alternative_paths = pathfinding.build_alternative_paths(minimum_cost)
            simulation = Simulation(map, paths, alternative_paths, minimum_cost)

        except EmptyFile as e:
            print(e)
        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except InvalidConfiguration as e:
            print(f"Invalid configuration: {e}")
    else:
        print("Error in arguments provided."
              " Usage: python3 fly_in.py <map.txt>")

if __name__ == "__main__":
    main()
