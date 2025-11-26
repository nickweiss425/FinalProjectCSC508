# Protocol lets us express an interface without enforcing inheritence
from typing import Any, Dict, List, Protocol
import threading
from gaze_event import GazeEvent
from fixation_event import FixationEvent
from robot_command import RobotCommand, CommandType

# any class with an update(data) method is considered an Observer --> mirrors java implementation
class Observer(Protocol):
    def update(self, data: Dict[str, Any]) -> None:
        pass

class Blackboard:
    # instance stores the one and only Blackboard object
    _instance = None

    # ensures thread safety during instance creation
    _lock = threading.Lock()

    _initialized = False

    def __new__(cls):
        """
        __new__ is called before __init__.
        Enforce Singleton: only create one instance of Blackboard.
        """
        # singleton pattern
        if cls._instance is None:
            with cls._lock:
                # create new instance if not initialized before
                cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        intialize instance fields only once.
        subsequent calls to Blackboard() will return the same instance
        and skip this initialization block
        """
        if self._initialized:
            return
        
        # latest raw gaze sample (not averaged) --> used by GUI to draw dot in real time
        self._current_gaze: GazeEvent = None
        
        # data structure containing information about the past window of data collected
        self._current_fixation: FixationEvent = None

        # holds the last issued command to the robot
        self._current_command: RobotCommand = None

        self._observers: List[Observer] = []
        self._data_lock = threading.Lock()
        self._initialized = True
    
    @classmethod 
    def get_instance(cls):
        """
        Java-style Singleton accessor
        Can use get_instance() instead of Blackboard() --> makes it more like java
        """

        # when cls() is caled, then __new__ is called --> returns the same object
        # every time (singleton)
        return cls()
    
    # --------- Private class methods ---------
    def _get_data_snapshot(self) -> Dict[str, Any]:
        """
        Build a snapshot of the current data state
        Should only call this when holding _data_lock
        """
        # package all the important data in the blackboard
        return{
            "current_gaze": self._current_gaze,
            "current_fixation": self._current_fixation,
            "current_command": self._current_command
        }
    
    def _notify_observers(self, snapshot: Dict[str, Any]):
        """
        notify all observers with the given snapshot
        Copies the observer list under lock to avoid concurrent modification issues.
        """
        with self._data_lock:
            observers_copy = list(self._observers)  # shallow copy

        for observer in observers_copy:
            observer.update(snapshot)

    # --------- observer registration ---------
    def add_observer(self, observer: Observer):
        """register an observer to receive updates"""
        with self._data_lock:
            self._observers.append(observer)

    def remove_observer(self, observer: Observer):
        """unregister an observer so it doesnt receive updates anymore"""
        with self._data_lock:
            if observer in self._observers:
                self._observers.remove(observer)

    # --------- setters ---------
    def set_current_gaze(self, gaze: GazeEvent):
        """
        current gaze setter
        also notify all observers
        """
        with self._data_lock:
            self._current_gaze = gaze
            snapshot = self._get_data_snapshot()
        self._notify_observers(snapshot)

    def set_current_fixation(self, fixation: FixationEvent):
        """
        current fixation setter
        also notify all observers
        """
        with self._data_lock:
            self._current_fixation = fixation
            snapshot = self._get_data_snapshot()
        self._notify_observers(snapshot)

    def set_current_command(self, command: RobotCommand):
        """
        current command setter
        also notify all observers
        """
        with self._data_lock:
            self._current_command = command
            snapshot = self._get_data_snapshot()
        self._notify_observers(snapshot)   

    # --------- getters (if needed by non-observer code) ---------
    def get_current_gaze(self):
        with self._data_lock:
            return self._current_gaze

    def get_current_fixation(self):
        with self._data_lock:
            return self._current_fixation

    def get_current_command(self):
        with self._data_lock:
            return self._current_command