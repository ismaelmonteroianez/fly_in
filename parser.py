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
    """
    Validate that a value is a positive integer.
    Args:
        value: String value to validate.
    Raises:
        InvalidConfiguration: If the value is not a positive integer.
    """
    try:
        num = int(value)
    except ValueError:
        raise InvalidConfiguration("Value must be a positive integer")
    if num <= 0:
        raise InvalidConfiguration("Value must be a positive integer")


def check_integer(value: str, index: int) -> None:
    """
    Validate that a value can be converted to an integer.
    Args:
        value: String value representing the integer.
        index: Line number of the value in the configuration file.
    Raises:
        InvalidConfiguration: If the value is not an integer.
    """
    try:
        int(value)
    except ValueError:
        raise InvalidConfiguration(f"Line {index}: Coordinates"
                                   " must be integers")


def check_hub_name(hub_name: str, index: int) -> None:
    """
    Validate that a hub name does not contain a dash.
    Args:
        hub_name: Name of the hub to validate.
        index: Line number of the hub in the configuration file.
    Raises:
        InvalidConfiguration: If the hub name contains a dash.
    """
    for character in hub_name:
        if character == "-":
            raise InvalidConfiguration(f"Line {index}: Hub"
                                       " names cannot contain '-'")


def parser_number_drones(index, drone_parts: list[str]) -> int:
    """
    Parse and validate the number of drones from a configuration line.
    Args:
        index: Line number containing the drone configuration.
        drone_parts: Parts of the drone configuration split by a colon.
    Returns:
        The validated number of drones.
    Raises:
        InvalidConfiguration: If the drone configuration has an invalid
            format or contains a non-positive integer.
    """
    if len(drone_parts) == 2:
        drone_parameter = drone_parts[1].strip()
        check_positive_int(drone_parameter)
        nbr_drones = int(drone_parameter)
        return nbr_drones
    else:
        raise InvalidConfiguration(f"Line {index}: invalid number of drones")


def split_metadata(line: str, index: int) -> tuple[str, str | None]:
    """
    Separate the main content of a line from its metadata.
    Args:
        line: Configuration line containing optional metadata.
        index: Line number of the configuration line.
    Returns:
        A tuple containing the main content and the metadata content.
        The metadata value is None when no metadata is present.
    Raises:
        InvalidConfiguration: If the metadata brackets or format are invalid.
    """
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
    """
    Parse and validate metadata associated with a hub.
    Args:
        metadata: Metadata string containing hub attributes.
        index: Line number of the hub in the configuration file.
    Returns:
        A dictionary containing the zone type, color, and maximum
        drone capacity of the hub.
    Raises:
        InvalidConfiguration: If the metadata format, key, value,
            zone type, or capacity is invalid.
    """
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
    """
    Parse and validate a hub definition.
    Args:
        hub: Configuration line defining a hub.
        index: Line number of the hub in the configuration file.
    Returns:
        A dictionary containing the hub name, coordinates, and metadata.
    Raises:
        InvalidConfiguration: If the hub format, name, coordinates,
            or metadata is invalid.
    """
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
    """
    Parse and validate connection metadata.
    Args:
        metadata: Metadata string containing connection attributes.
        index: Line number of the connection in the configuration file.
    Returns:
        The maximum number of drones allowed on the connection.
    Raises:
        InvalidConfiguration: If the metadata format, key, value,
            or capacity is invalid.
    """
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
    """
    Parse and validate a connection definition.
    Args:
        connection: Configuration line defining a connection.
        index: Line number of the connection in the configuration file.
    Returns:
        A dictionary containing the two connected zones and their
        maximum link capacity.
    Raises:
        InvalidConfiguration: If the connection format, zone names,
            or metadata is invalid.
    """
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
    """
    Parse all hub and connection definitions after the drone count.
    Args:
        content_list: List of configuration lines paired with their
            original line numbers.
    Returns:
        A tuple containing a dictionary of hubs and a list of connections.
    Raises:
        InvalidConfiguration: If a hub or connection is invalid, duplicated,
            declared before its zones, or if the configuration does not
            contain exactly one start hub and one end hub.
    """
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
    """
    Parse a drone configuration file.
    The parser reads the configuration file, removes comments and empty
    lines, validates the drone count, hubs, connections, and metadata,
    and returns the complete configuration.
    Args:
        file_path: Path to the configuration file.
    Returns:
        A dictionary containing the number of drones, hubs, and connections.
    Raises:
        EmptyFile: If the configuration file is empty.
        InvalidConfiguration: If the file contains invalid or incomplete
            configuration data.
        FileNotFoundError: If the specified file does not exist.
    """
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
    hubs, connections = parse_remaining_lines(content_list)
    configuration = {
                    "nb_drones": nbr_drones,
                    "hubs": hubs,
                    "connections": connections
                    }
    return configuration
