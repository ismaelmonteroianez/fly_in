from parser import parser, EmptyFile, InvalidConfiguration
import sys
from simulation import Simulation
from map import Map
from pathfinding import Pathfinding

def main() -> None:
    if len(sys.argv) == 2:
        file_path = sys.argv[1]

        if not file_path.lower().endswith(".txt"):
            print("Invalid file type: expected a .txt file")
            return
        try:
            configuration = parser(file_path)
            print(configuration)
            map = Map(configuration)
            pathfinding = Pathfinding(map)
            previous, costs = pathfinding.find_path()
            paths = pathfinding.build_paths(previous)
            paths = pathfinding.reverse_paths(paths)
            alternative_paths = pathfinding.build_alternative_paths(costs[map.get_end_hub().name])
            simulation = Simulation(map, paths, alternative_paths)
            turns = simulation.calculate_turns(simulation.paths_assigned)
            print()
            print("Paths:", paths)
            print("Turns:", turns)

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
