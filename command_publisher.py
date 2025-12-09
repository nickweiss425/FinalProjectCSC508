# mqtt_command_publisher.py

from typing import Any, Dict, Optional

import paho.mqtt.client as mqtt

from blackboard import Blackboard, Observer
from robot_command import RobotCommand


class MqttCommandPublisher(Observer):
    """
    Observes Blackboard.current_command and publishes the command name
    to an MQTT topic, e.g. "gaze_bot/command".
    """

    def __init__(
        self,
        blackboard: Blackboard,
        broker_host: str = "test.mosquitto.org",
        broker_port: int = 1883,
        topic: str = "gaze_bot/command",
    ) -> None:
        self._blackboard = blackboard
        self._topic = topic

        self._client = mqtt.Client()
        self._client.connect(broker_host, broker_port, keepalive=60)
        # Run MQTT network loop in background thread
        self._client.loop_start()

    def update(self, data: Dict[str, Any]) -> None:
        """
        Called by Blackboard whenever its state changes.
        We only care when "current_command" is updated.
        """
        if data.get("changed") != "current_command":
            return

        cmd: Optional[RobotCommand] = data.get("current_command")
        if cmd is None:
            return

        # Send the enum NAME, e.g. "FORWARD", "LEFT"
        payload = cmd.command.name

        # Fire-and-forget publish
        self._client.publish(self._topic, payload)

    def close(self) -> None:
        """Cleanly stop the MQTT loop and disconnect."""
        self._client.loop_stop()
        self._client.disconnect()
