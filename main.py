from blackboard import Blackboard
from gaze_source import GazeSource
from gaze_interpreter import GazeInterpreter
from command_generator import CommandGenerator

def main():
    blackboard = Blackboard.get_instance()

    generator = CommandGenerator(blackboard)
    blackboard.add_observer(generator)

    interpreter = GazeInterpreter(blackboard, window_duration=1.5, min_samples=5, std_threshold=0.06)
    blackboard.add_observer(interpreter)

    gaze_source = GazeSource(blackboard, poll_interval=0.03)
    gaze_source.start()

    while(True):
        pass

if __name__ == "__main__":
    main()