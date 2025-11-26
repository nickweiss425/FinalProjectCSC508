from dataclasses import dataclass
from enum import Enum
from time import time


class CommandType(Enum):
    """high-level commands for the robot"""
    FORWARD = "forward"
    BACKWARD = "backward"
    ROTATE_LEFT = "rotate_left"
    ROTATE_RIGHT = "rotate_right"
    STOP = "stop"


@dataclass
class RobotCommand:
    """
    wrapper for a robot command
    """
    command: CommandType
    timestamp: float = time()

