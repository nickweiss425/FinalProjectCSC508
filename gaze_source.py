import threading
import time
from typing import Optional

from gaze_event import GazeEvent
from blackboard import Blackboard

from eyetrax import GazeEstimator, run_9_point_calibration
import cv2

# runs on own thread and talks to eyetrax library 
# publishes eye tracking data to blackboard
class GazeSource(threading.Thread):
    """
    runs on own thread that continuously reads gaze data from  gaze library
    and publishes it to the Blackboard as GazeEvent objects
    """

    def __init__(self, blackboard, poll_interval=0.03):
        # daemon=True means thread exits when main exits
        super().__init__(daemon=True)   

        self._poll_interval = poll_interval

        self._blackboard = blackboard

        # boolean to keep track of running status --> allows for a safe exit
        self._running = False

        self._estimator = None
        self._cap = None

    
    def start(self):
        """
        start the gaze source thread
        override start() only to set the _running flag before the thread begins
        """
        self._running = True
        super().start()

    def stop(self):
        """
        signal the thread to stop on the next loop iteratio
        """
        self._running = False

    def calibrate(self):
        self._estimator = GazeEstimator()
        run_9_point_calibration(self._estimator)

    def run(self):
        """
        thread loop:
        - read a gaze sample from the gaze library
        - wrap it in a GazeEvent
        - push it to the Blackboard
        - sleep for poll_interval
        """

        # Save model
        self._estimator.save_model("gaze_model.pkl")

        # Load model
        self._estimator.load_model("gaze_model.pkl")

        self._cap = cv2.VideoCapture(0)
        
        while self._running:
            event = self._read_gaze_event()
            if event is not None:
                self._blackboard.set_current_gaze(event)

            # avoid busy-waiting; control sampling rate
            time.sleep(self._poll_interval)


    def _read_gaze_event(self):
        """
        read a single frame from the camera, run eyetrax on it,
        and return a GazeEvent or None if no valid gaze
        """
        ret, frame = self._cap.read()
        features, blink = self._estimator.extract_features(frame)

        # predict screen coordinates
        if features is not None and not blink:
            x, y = self._estimator.predict([features])[0]
            norm_x = float(x) / 1000.0
            norm_y = float(y) / 1000.0
            #print(f"Gaze: ({x:.3f}, {y:.3f})")
            ge = GazeEvent(x=norm_x, y=norm_y, timestamp=time.time())
            return ge
        return None


    