from drone import Drone
from hub import Hub
from connection import Connection
from simulation import Simulation
from pathfinding import Pathfinding


class DroneController:

    def __init__(self, simulation: Simulation):
            self.simulation = simulation
