import time
import math
from typing import Any, Dict, List, Protocol
import statistics

from gaze_event import GazeEvent
from fixation_event import FixationEvent
from robot_command import RobotCommand, CommandType
from blackboard import Blackboard, Observer


class CommandGenerator(Observer):
    def __init__(self, blackboard: Blackboard):
        self._blackboard = blackboard

    def update(self, data: Dict[str, Any]):
        """
        called by the Blackboard when its state changes.
        react only when current_fixation was updated
        """
    
        if (data.get("changed") == "current_fixation"):
            print(data)
            fixation = data.get("current_fixation")
            new_command_type = self._fixation_to_command(fixation)
            if new_command_type is not None:
                new_command = RobotCommand(new_command_type, time.time())
                last_command = self._blackboard.get_current_command()

                if last_command is None or new_command != last_command:
                    self._blackboard.set_current_command(new_command)
                    print("NEW COMMAND: " + str(new_command.command))
    
    def _fixation_to_command(self, fixation: FixationEvent):
        """
        Convert a FixationEvent into one of the five CommandTypes using:
        - diagonals y = x and y = -x + 1 to split into 4 wedges:
          top wedge    --> FORWARD
          bottom wedge --> BACKWARD
          left wedge   --> LEFT
          right wedge  --> RIGHT
        """

        if not fixation.is_valid:
            return CommandType.STOP
        
        x = fixation.mean_x
        y = fixation.mean_y

        
        positive_cross = x 
        negative_cross = -1 * x + 1
        
        if (x < 0.5 and y <= positive_cross) or (x >= 0.5 and y <= negative_cross):
            return CommandType.FORWARD
        
        if (x < 0.5 and y < negative_cross and y > positive_cross):
            return CommandType.LEFT
        
        if (x > 0.5 and y < positive_cross and y > negative_cross):
            return CommandType.RIGHT
        
        if (x < 0.5 and y >= negative_cross) or (x >= 0.5 and y >= positive_cross):
            return CommandType.BACKWARD
        
        return None


