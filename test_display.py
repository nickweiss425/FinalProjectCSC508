from blackboard import Blackboard
from gaze_source import GazeSource
from gaze_interpreter import GazeInterpreter
from command_generator import CommandGenerator
from gaze_display import GazeDisplay
from fixation_event import FixationEvent

def main():
    blackboard = Blackboard.get_instance()


    display = GazeDisplay(blackboard)
    blackboard.add_observer(display)

    blackboard.set_current_command("UP")
    blackboard.set_current_gaze((50, 50))
    blackboard.set_current_fixation(FixationEvent(10, 10, 0.1, 0.1, 0.0, 1.0, True))
   

    display.run()

if __name__ == "__main__":
    main()
ß