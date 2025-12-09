# robot_game_client.py

import random
import queue
from dataclasses import dataclass
from typing import Optional

import paho.mqtt.client as mqtt
import tkinter as tk


GRID_SIZE = 10      # 10x10 grid
CELL_SIZE = 40      # pixels per cell


@dataclass
class RobotState:
    x: int
    y: int
    score: int = 0
    token_x: int = 0
    token_y: int = 0


class RobotGame:
    def __init__(self, broker_host: str = "test.mosquitto.org", broker_port: int = 1883, topic: str = "gaze_bot/command"):
        self._root = tk.Tk()
        self._root.title("MQTT Robot Game")

        width = GRID_SIZE * CELL_SIZE
        height = GRID_SIZE * CELL_SIZE

        self._canvas = tk.Canvas(self._root, width=width, height=height, bg="white")
        self._canvas.pack()

        self._status_label = tk.Label(self._root, text="Score: 0")
        self._status_label.pack()

        # queue of commands received from MQTT
        self._cmd_queue: "queue.SimpleQueue[str]" = queue.SimpleQueue()

        # initial robot state (start in the middle)
        self._state = RobotState(
            x=GRID_SIZE // 2,
            y=GRID_SIZE // 2,
        )
        self._place_new_token()

        # draw static grid lines
        self._draw_grid()

        # set up MQTT
        self._client = mqtt.Client()
        self._client.on_message = self._on_mqtt_message
        self._client.connect(broker_host, broker_port, keepalive=60)
        self._client.subscribe(topic)
        self._client.loop_start()

        # start periodic Tk polling of the command queue
        self._root.after(50, self._process_commands)

        # initial draw
        self._draw_scene()

    
    # MQTT callback
    def _on_mqtt_message(self, client, userdata, message) -> None:
        cmd_str = message.payload.decode().strip().upper()
        self._cmd_queue.put(cmd_str)

    # ------------- Game logic -------------

    def _process_commands(self) -> None:
        """
        periodically called in Tk mainloop to apply any commands
        received via MQTT
        """
        while not self._cmd_queue.empty():
            try:
                cmd = self._cmd_queue.get_nowait()
            except queue.Empty:
                break
            self._apply_command(cmd)

        self._draw_scene()
        self._root.after(50, self._process_commands)

    def _apply_command(self, cmd: str) -> None:
        """
        interpret FORWARD/BACKWARD/LEFT/RIGHT/STOP and update robot state
        """
         # up
        if cmd == "FORWARD":
            self._move(0, -1)    
        # down 
        elif cmd == "BACKWARD":
            self._move(0, 1)   
        # left    
        elif cmd == "LEFT":
            self._move(-1, 0) 
        # right     
        elif cmd == "RIGHT":
            self._move(1, 0)
        # do nothing, robot stays put       
        elif cmd == "STOP":
            
            pass

        # check token capture
        if self._state.x == self._state.token_x and self._state.y == self._state.token_y:
            self._state.score += 1
            self._place_new_token()

    def _move(self, dx: int, dy: int) -> None:
        """
        move the robot one cell in the given direction
        """
        new_x = max(0, min(GRID_SIZE - 1, self._state.x + dx))
        new_y = max(0, min(GRID_SIZE - 1, self._state.y + dy))

        self._state.x = new_x
        self._state.y = new_y

    def _place_new_token(self) -> None:
        """place the token at a random cell different from the robot's current cell"""
        while True:
            tx = random.randint(0, GRID_SIZE - 1)
            ty = random.randint(0, GRID_SIZE - 1)
            if tx != self._state.x or ty != self._state.y:
                self._state.token_x = tx
                self._state.token_y = ty
                break

    # ------------- Drawing -------------

    def _draw_grid(self) -> None:
        for i in range(GRID_SIZE + 1):
            # vertical lines
            x = i * CELL_SIZE
            self._canvas.create_line(x, 0, x, GRID_SIZE * CELL_SIZE, fill="#ddd")
            # horizontal lines
            y = i * CELL_SIZE
            self._canvas.create_line(0, y, GRID_SIZE * CELL_SIZE, y, fill="#ddd")

    def _draw_scene(self) -> None:
        self._canvas.delete("robot")
        self._canvas.delete("token")

        # draw token
        tx = self._state.token_x * CELL_SIZE
        ty = self._state.token_y * CELL_SIZE
        self._canvas.create_rectangle(
            tx + 5,
            ty + 5,
            tx + CELL_SIZE - 5,
            ty + CELL_SIZE - 5,
            fill="orange",
            tags="token",
        )

        # draw robot as a circle
        rx = self._state.x * CELL_SIZE
        ry = self._state.y * CELL_SIZE
        self._canvas.create_oval(
            rx + 8,
            ry + 8,
            rx + CELL_SIZE - 8,
            ry + CELL_SIZE - 8,
            fill="blue",
            tags="robot",
        )

        # Update score label
        self._status_label.config(text=f"Score: {self._state.score}")


    def run(self) -> None:
        self._root.mainloop()

    def close(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()
        self._root.destroy()


def main():
    game = RobotGame()
    try:
        game.run()
    finally:
        game.close()


if __name__ == "__main__":
    main()
