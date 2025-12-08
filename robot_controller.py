import time
import math
from typing import Any, Dict, List, Protocol
import statistics

from gaze_event import GazeEvent
from fixation_event import FixationEvent
from robot_command import RobotCommand, CommandType
from blackboard import Blackboard, Observer

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class RobotController(Observer):
    def __init__(self, blackboard: Blackboard):
        self._blackboard = blackboard


    def update(self, data: dict[str, Any]):

        if data.get("changed") == "current_command":
            new_command = data.get("current_command")
            self._send_command(new_command)
    
    def _send_command(self, command: RobotCommand):
        """
        command: one of 'FORWARD', 'BACKWARD', 'ROTATE_LEFT',
                 'ROTATE_RIGHT', 'STOP'
        speed:   linear or angular magnitude (rad/s for rotation)
        """

        command = command.command

        cmd = command.upper().strip()
        twist = Twist()

        if cmd == 'FORWARD':
            twist.linear.x = speed      # move forward
            twist.angular.z = 0.0
        elif cmd == 'BACKWARD':
            twist.linear.x = -speed     # move backwards
            twist.angular.z = 0.0
        elif cmd == 'ROTATE_LEFT':
            twist.linear.x = 0.0
            twist.angular.z = speed     # rotate CCW
        elif cmd == 'ROTATE_RIGHT':
            twist.linear.x = 0.0
            twist.angular.z = -speed    # rotate CW
        elif cmd == 'STOP':
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        else:
            self.get_logger().warn(f"Unknown command: {command}")
            return

        self.cmd_vel_pub.publish(twist)
        self.get_logger().info(f"Sent command: {cmd} (speed={speed})")
