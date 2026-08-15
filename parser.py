class EmptyFile(Exception):
    """
    Exception raised when the configuration file is empty.
    Used to prevent the program from running without valid input data.
    """
    pass


class InvalidConfiguration(Exception):
    """
    Exception raised when the configuration file contains invalid values.
    This includes malformed parameters, out-of-range values, or
    logically inconsistent configuration settings.
    """
    pass


def check_positive_int(value: str) -> None:
    try:
        num = int(value)
    except ValueError:
        raise InvalidConfiguration("Value must be a positive integer")
    if num <= 0:
        raise InvalidConfiguration("Value must be a positive integer")


def check_integer(value: str, index: int) -> None:
    try:
        int(value)
    except ValueError:
        raise InvalidConfiguration(f"Line {index}: Coordinates"
                                   " must be integers")


def check_hub_name(hub_name: str, index: int) -> None:
    for character in hub_name:
        if character == "-":
            raise InvalidConfiguration(f"Line {index}: Hub"
                                       " names cannot contain '-'")


def parser_number_drones(index, drone_parts: list[str]) -> int:
    if len(drone_parts) == 2:
        drone_parameter = drone_parts[1].strip()
        check_positive_int(drone_parameter)
        nbr_drones = int(drone_parameter)
        return nbr_drones
    else:
        raise InvalidConfiguration(f"Line {index}: invalid number of drones")


def split_metadata(line: str, index: int) -> tuple[str, str | None]:
    if line.count("[") > 1:
        raise InvalidConfiguration(f"Line {index}: Invalid metadata format")
    if line.count("]") != line.count("["):
        raise InvalidConfiguration(f"Line {index}: Invalid metadata brackets")
    if "[" in line:
        main_part, metadata_part = line.split("[")
        metadata_content, extra_trash = metadata_part.split("]")
        if metadata_content.strip() == "":
            raise InvalidConfiguration(f"Line {index}: Invalid"
                                       " metadata format")
        if extra_trash.strip() != "":
            raise InvalidConfiguration(f"Line {index}: Invalid"
                                       " metadata format")
        metadata_part = metadata_content
    else:
        main_part = line
        metadata_part = None
    return main_part, metadata_part


def parse_hub_metadata(metadata: str, index: int) -> dict[str, str | int]:
    metadata_parts = metadata.split()
    duplicate_list_keys = []
    metadata_data = {
                    "zone": "normal",
                    "color": "none",
                    "max_drones": 1
                    }
    for part in metadata_parts:
        if part.count("=") != 1:
            raise InvalidConfiguration(f"Line {index}: Number of '=' in"
                                       " metadata must be 1 for each element")
        parts = part.split("=")
        key, value = parts
        if key == "" or value == "":
            raise InvalidConfiguration(f"Line {index}: Metadata"
                                       " element must be key=value only")
        if key in duplicate_list_keys:
            raise InvalidConfiguration(f"Line {index}: "
                                       "duplicated metadata key")
        else:
            duplicate_list_keys.append(key)
        if key == "zone":
            if value not in ["normal", "blocked", "restricted", "priority"]:
                raise InvalidConfiguration(f"Line {index}: "
                                           "Zone information must be normal, "
                                           "blocked, restricted "
                                           "or priority only")
            metadata_data["zone"] = value
        elif key == "color":
            metadata_data["color"] = value
        elif key == "max_drones":
            check_positive_int(value)
            metadata_data["max_drones"] = int(value)
        else:
            raise InvalidConfiguration(f"Line {index}: Metadata key "
                                       "must be zone, color or max_drones")
    return metadata_data


def parse_hub(hub: str, index: int) -> dict[str, object]:
    metadata_data = {
                    "zone": "normal",
                    "color": "none",
                    "max_drones": 1
                    }
    main_part, metadata_part = split_metadata(hub, index)
    main_parts = main_part.split(":")
    if len(main_parts) != 2:
        raise InvalidConfiguration(f"Line {index}: Invalid hub format")
    _, hub_content = main_parts
    parts = hub_content.strip().split()
    if len(parts) != 3:
        raise InvalidConfiguration(f"Line {index}: Invalid hub format")
    hub_name, x, y = parts
    check_hub_name(hub_name, index)
    check_integer(x, index)
    check_integer(y, index)
    if metadata_part is not None:
        metadata_data = parse_hub_metadata(metadata_part, index)
    hub_data = {
            "name": hub_name,
            "x": int(x),
            "y": int(y),
            "metadata": metadata_data
          }
    return hub_data


def parse_connection_metadata(metadata: str, index: int) -> int:
    max_link_capacity = 1
    metadata_parts = metadata.split()
    duplicate_list_keys = []
    for metadata_part in metadata_parts:
        if metadata_part.count("=") != 1:
            raise InvalidConfiguration(f"Line {index}: Number of "
                                       "'=' in metadata must "
                                       "be 1 for each element")
        parts = metadata_part.split("=")
        key, value = parts
        if key == "" or value == "":
            raise InvalidConfiguration(f"Line {index}: "
                                       "Metadata element "
                                       "must be key=value only")
        if key in duplicate_list_keys:
            raise InvalidConfiguration(f"Line {index}: "
                                       "duplicated metadata key")
        else:
            duplicate_list_keys.append(key)
        if key == "max_link_capacity":
            check_positive_int(value)
            max_link_capacity = int(value)
        else:
            raise InvalidConfiguration(f"Line {index}: "
                                       "Metadata key for "
                                       "connections must be "
                                       "max_link_capacity")
    return max_link_capacity


def parse_connection(connection: str, index: int) -> dict[str, str | int]:
    max_link_capacity = 1
    main_part, metadata_part = split_metadata(connection, index)
    main_parts = main_part.split(":")
    if len(main_parts) != 2:
        raise InvalidConfiguration(f"Line {index}: Invalid connection format")
    _, connection_content = main_parts
    connection_parts = connection_content.split("-")
    if len(connection_parts) != 2:
        raise InvalidConfiguration(f"Line {index}: Invalid connection format")
    zone1 = connection_parts[0].strip()
    zone2 = connection_parts[1].strip()
    if zone1 == "" or zone2 == "":
        raise InvalidConfiguration(f"Line {index}: Invalid connection format")
    if zone1 == zone2:
        raise InvalidConfiguration(f"Line {index}: "
                                   "Connection cannot link a zone to itself")
    if metadata_part is not None:
        max_link_capacity = parse_connection_metadata(metadata_part, index)
    connection_data = {
        "zone1": zone1,
        "zone2": zone2,
        "max_link_capacity": max_link_capacity
    }
    return connection_data


def parse_remaining_lines(content_list: list[tuple[int, str]]) -> tuple[dict, list]:
    hubs = {}
    connections = []
    start_hub_count = 0
    end_hub_count = 0
    for index, line in content_list[1:]:
        if line.startswith("start_hub:"):
            hub_data = parse_hub(line, index)
            if hub_data["name"] in hubs:
                raise InvalidConfiguration(f"Line {index}: "
                                           "Duplicated hub name")
            hub_data["type"] = "start"
            hubs[hub_data["name"]] = hub_data
            start_hub_count += 1
        elif line.startswith("end_hub:"):
            hub_data = parse_hub(line, index)
            if hub_data["name"] in hubs:
                raise InvalidConfiguration(f"Line {index}: "
                                           "Duplicated hub name")
            hub_data["type"] = "end"
            hubs[hub_data["name"]] = hub_data
            end_hub_count += 1
        elif line.startswith("hub:"):
            hub_data = parse_hub(line, index)
            if hub_data["name"] in hubs:
                raise InvalidConfiguration(f"Line {index}: "
                                           "Duplicated hub name")
            hub_data["type"] = "hub"
            hubs[hub_data["name"]] = hub_data
        elif line.startswith("connection:"):
            connection_data = parse_connection(line, index)
            if connection_data["zone1"] not in hubs or connection_data["zone2"] not in hubs:
                raise InvalidConfiguration(f"Line {index}: Conexion declared before zone in file")
            for connection in connections:
                if ((connection["zone1"] == connection_data["zone1"] and connection["zone2"] == connection_data["zone2"]) or
                    (connection["zone2"] == connection_data["zone1"] and connection["zone1"] == connection_data["zone2"])):
                    raise InvalidConfiguration(f"Line {index}: Duplicated connection")
            connections.append(connection_data)
        else:
            raise InvalidConfiguration(f"Line {index}: "
                                       "Invalid line format: "
                                       "expected start_hub, "
                                       "end_hub, hub or connection")
    if start_hub_count != 1 or end_hub_count != 1:
        raise InvalidConfiguration("Configuration must contain "
                                   "exactly one start_hub "
                                   "and one end_hub")
    return hubs, connections


def parser(file_path: str) -> dict[str, object]:
    content_list: list[tuple[int, str]] = []
    with open(file_path, "r") as f:
        content = f.read()
    if content.strip() == "":
        raise EmptyFile("Error: empty file")
    lines = content.split("\n")
    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        if line.startswith("#") or line == "":
            continue
        content_list.append((line_number, line))
    if content_list == []:
        raise InvalidConfiguration("Error: file contains only comments")
    if not content_list[0][1].startswith("nb_drones:"):
        raise InvalidConfiguration("Error: line number of "
                                   "drones(nb_drones) not "
                                   "found or out of place")
    else:
        drone_parameters = content_list[0][1].split(":")
        nbr_drones = parser_number_drones(content_list[0][0], drone_parameters)
        if nbr_drones > 50:
            raise InvalidConfiguration("Number of drones must at most 50")
    hubs, connections = parse_remaining_lines(content_list)
    configuration = {
                    "nb_drones": nbr_drones,
                    "hubs": hubs,
                    "connections": connections
                    }
    return configuration
