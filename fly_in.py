from parser import parser, EmptyFile, InvalidConfiguration
import sys


def main() -> None:
    if len(sys.argv) == 2:
        file_path = sys.argv[1]

        if not file_path.lower().endswith(".txt"):
            print("Invalid file type: expected a .txt file")
            return
        try:
            configuration = parser(file_path)
            print(configuration)
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