import time
import math
from typing import Any, Dict, List, Protocol
import statistics

from gaze_event import GazeEvent
from fixation_event import FixationEvent
from robot_command import RobotCommand, CommandType
from blackboard import Blackboard, Observer


class RobotController(Observer):
