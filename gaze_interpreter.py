import time
import math
from typing import Any, Dict, List, Protocol
import statistics

from gaze_event import GazeEvent
from fixation_event import FixationEvent
from robot_command import RobotCommand, CommandType
from blackboard import Blackboard, Observer



# tracks updates to gaze events in blackboard and converts window into fixation event
class GazeInterpreter(Observer):

    def __init__(self, blackboard, window_duration=0.6, min_samples=5, std_threshold=0.05):
        """
        initialize the gaze interpreter

        :param blackboard: Shared Blackboard instance for setting fixation events
        :param window_duration: required time span (in seconds) of gaze samples
                                needed to compute a fixation
        :param min_samples: minimum number of gaze samples required to attempt
                            fixation creation
        :param std_threshold: max allowed standard deviation in x and y for
                              a fixation to be considered valid
        """

        self._blackboard = blackboard

        self._window_duration = window_duration

        self._min_samples = min_samples

        self._std_threshold = std_threshold

        self._samples = []

    def update(self, data: Dict[str, Any]):
        """
        called by the blackboard whenever its state changes

        listen for new raw gaze events under the key "current_gaze",
        append them to our sliding window, and compute a FixationEvent once
        the window has enough time span and enough samples
        """
        if (data.get("changed") == "current_gaze"):
            gaze = data.get("current_gaze")

            if (gaze is not None):
                self._samples.append(gaze)

                if (self._window_ready()):
                    fixation = self._compute_fixation()
                    if (fixation is not None):
                        self._blackboard.set_current_fixation(fixation)
                        print(fixation)
                        self._samples = []

    def _window_ready(self):
        """
        return True if:
        - there are enough gaze samples
        - the time span between the earliest and latest sample
          is at least window_duration
        """

        if (len(self._samples) > 1):
            latest_time = self._samples[-1].timestamp
            earliest_time = self._samples[0].timestamp
            diff = latest_time - earliest_time
            if (diff >= self._window_duration and len(self._samples) >= self._min_samples):
                return True
        return False
    
    def _compute_fixation(self):
        """
        compute the mean and standard deviation of x and y values across the
        current sliding window then build a FixationEvent

        returns None if something is inconsistent
        """
        if (len(self._samples) < 2):
            return None

        xs = [sample.x for sample in self._samples]
        ys = [sample.y for sample in self._samples]
        mean_x = statistics.mean(xs)
        mean_y = statistics.mean(ys)
        std_x = statistics.stdev(xs)
        std_y = statistics.stdev(ys)
        if (std_x > self._std_threshold or std_y > self._std_threshold):
            valid = False
        else:
            valid = True

        fixation = FixationEvent(mean_x=mean_x, 
                                 mean_y=mean_y, 
                                 std_x=std_x, 
                                 std_y=std_y, 
                                 start_time=self._samples[0].timestamp, 
                                 end_time=self._samples[-1].timestamp, 
                                 is_valid=valid)
        
        return fixation
        
        
