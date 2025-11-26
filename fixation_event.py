from dataclasses import dataclass

@dataclass
class FixationEvent:
    """
    represents a fixation sample --> gazes sampled over a window of time
    """
    mean_x: float
    mean_y: float
    std_x: float
    std_y: float
    start_time: float
    end_time: float
    is_valid: bool