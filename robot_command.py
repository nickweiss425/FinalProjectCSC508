from dataclasses import dataclass
from enum import Enum
from time import time


class CommandType(Enum):
    """high-level commands for the robot"""
    FORWARD = "forward"
    BACKWARD = "backward"
    LEFT = "left"
    RIGHT = "right"
    STOP = "stop"


@dataclass
class RobotCommand:
    """
    wrapper for a robot command
    """
    command: CommandType
    timestamp: float = time()

