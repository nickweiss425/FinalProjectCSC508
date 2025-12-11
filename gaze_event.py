from dataclasses import dataclass

@dataclass
class GazeEvent:
    """
    represents a single gaze sample
    """
    x: float
    y: float
    timestamp: float
