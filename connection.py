from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from hub import Hub


class Connection():

    def __init__(self, source: "Hub", destination: "Hub", max_link_capacity: int):
        self.source = source
        self.destination = destination
        self.max_link_capacity = max_link_capacity


    def get_source(self) -> "Hub":
        return self.source


    def get_destination(self) -> "Hub":
        return self.destination


    def get_other_hub(self, hub: "Hub") -> "Hub | None":
        if hub == self.source:
            return self.destination
        elif hub == self.destination:
            return self.source
        else:
            return None


    def get_max_link_capacity(self) -> int:
        return self.max_link_capacity


    def __str__(self) -> str:
        return f"Connection {self.source.name} -> {self.destination.name} - capacity: {self.max_link_capacity}"
