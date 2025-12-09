from blackboard import Blackboard
from gaze_source import GazeSource
from gaze_interpreter import GazeInterpreter
from command_generator import CommandGenerator
from command_publisher import MqttCommandPublisher
from gaze_display import GazeDisplay
from screeninfo import get_monitors

def main():
    blackboard = Blackboard.get_instance()

    display = GazeDisplay()
    blackboard.add_observer(display)

    generator = CommandGenerator(blackboard)
    blackboard.add_observer(generator)

    interpreter = GazeInterpreter(blackboard, window_duration=1.5, min_samples=5, std_threshold=0.06)
    blackboard.add_observer(interpreter)

    mqtt_publisher = MqttCommandPublisher(blackboard)
    blackboard.add_observer(mqtt_publisher)

    gaze_source = GazeSource(blackboard, poll_interval=0.03)
    gaze_source.calibrate()
    gaze_source.start()

    def on_close():
        gaze_source.stop()
        display.root.destroy()

    display.root.protocol("WM_DELETE_WINDOW", on_close)

    display.run()

if __name__ == "__main__":
    main()