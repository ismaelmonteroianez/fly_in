from parser import parser, EmptyFile, InvalidConfiguration
import sys
import os
from drone_controller import DroneController

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
            drone_controller = DroneController(configuration)
            drone_controller.run()
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
