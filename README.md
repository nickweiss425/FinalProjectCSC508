# Eye-Controlled Robot Command System
Names: Charles Moreno and Nick Weiss  
This project uses a python eye tracking library to generate high-level robot commands, publishes them over MQTT, and visualizes both gaze and commands in a GUI. An optional MQTT “robot game” shows a dot moving on a grid in response to the commands.


### Prerequisites
- Python 3.9+ installed
- Internet connection (for the public MQTT broker)


### (Optional) Create and activate a virtual environment


```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```


### Install dependencies
```bash
pip install -r requirements.txt
```


### Run the main application (Gaze Tracking + GUI):
```bash
python3 main.py
```
This will:


Start the gaze-tracking thread (EyeTrax + OpenCV)


Normalize gaze data and compute fixations


Generate high-level robot commands


Publish robot commands to the MQTT topic gaze_bot/command


Open a fullscreen Tkinter GUI showing:


Red dot = live gaze


Text labels = interpreted command + gaze/fixation info




### Run the Robot Game (MQTT Subscriber):
In a second terminal, run:
```bash
python3 robot_game_client.py
```
This program:


Connects to the public MQTT broker test.mosquitto.org:1883


Listens for robot commands (FORWARD, BACKWARD, LEFT, RIGHT, STOP)


Moves a dot around a 10×10 grid


Lets you “capture” an orange token to increase score


This demonstrates multi-program communication and robot-control logic without requiring ROS2


### Project Structure:
```bash
main.py                   # Starts gaze tracking + GUI + command pipeline
blackboard.py             # Shared state & observer event hub
gaze_source.py            # EyeTrax + webcam gaze reader (threaded)
gaze_interpreter.py       # Gaze window --> FixationEvent
command_generator.py      # FixationEvent --> RobotCommand
mqtt_command_publisher.py # Publishes RobotCommand via MQTT
gaze_display.py           # Tkinter GUI visualizing gaze/fixation/command
robot_game_client.py      # Optional MQTT robot visualization mini-game
gaze_event.py             # GazeEvent dataclass
fixation_event.py         # FixationEvent dataclass
robot_command.py          # RobotCommand dataclass + enum
```
