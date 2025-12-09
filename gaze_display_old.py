# gaze_display.py
import tkinter as tk
import queue
from typing import Any, Dict

from blackboard import Blackboard  # adjust import if needed


class GazeDisplay:
    """
    Tkinter-based observer that passively displays:
      - the last gaze direction (from fixation or command)
      - the last robot command
    It does NOT accept any user input.
    """

    def __init__(self, blackboard: Blackboard):
        self.blackboard = blackboard

        # Queue for thread-safe communication from Blackboard threads to Tk mainloop
        self._queue: "queue.Queue[Dict[str, Any]]" = queue.Queue()

        # ---- Tkinter setup ----
        self.root = tk.Tk()
        self.root.title("Gaze & Command Display")


        self.root.attributes('-fullscreen', True)
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        self.center_x = self.width // 2
        self.center_y = self.height // 2
        
        self.root.rowconfigure(0, weight=1)   # canvas row expands
        self.root.rowconfigure(1, weight=0)   # bottom row stays natural height
        self.root.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg="white"
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        

        # ---- Diagonal lines ----
        self.canvas.create_line(
            0, 0, self.width, self.height,
            fill="black", width=2
        )
        self.canvas.create_line(
            self.width, 0, 0, self.height,
            fill="black", width=2
        )

        # Label regions
        self.canvas.create_text(self.center_x, self.center_y - self.center_y // 2,
                                text="FORWARD",
                                fill="black",
                                font=("Arial", 24, "bold"))
        self.canvas.create_text(self.center_x, self.center_y + self.center_y // 2,
                                text="BACKWARD",
                                fill="black",
                                font=("Arial", 24, "bold"))
        self.canvas.create_text(self.center_x - self.center_x // 2, self.center_y,
                                text="LEFT",
                                fill="black",
                                font=("Arial", 24, "bold"))
        self.canvas.create_text(self.center_x + self.center_x // 2, self.center_y,
                                text="RIGHT",
                                fill="black",
                                font=("Arial", 24, "bold"))

        # Predefined marker positions for each direction
        self.positions = {
            "FORWARD":    (self.center_x, self.center_y - self.center_y // 2),
            "BACKWARD":  (self.center_x, self.center_y + self.center_y // 2),
            "LEFT":  (self.center_x - self.center_x // 2, self.center_y),
            "RIGHT": (self.center_x + self.center_x // 2, self.center_y),
        }

        # Keep track of the last marker so we can remove it
        self.last_gaze_id = None
        self.last_fixation_id = None

        bottom_frame = tk.Frame(self.root)
        bottom_frame.grid(row=1, column=0, sticky="ew")
        bottom_frame.columnconfigure(0, weight=1)

        # Info labels below
        self.gaze_label = tk.Label(bottom_frame, text="Last gaze: (none)", font=("Arial", 12))
        self.gaze_label.pack()

        self.fixation_label = tk.Label(bottom_frame, text="Fixation around: (none)", font=("Arial", 12))
        self.fixation_label.pack()

        self.command_label = tk.Label(bottom_frame, text="Last command: (none)", font=("Arial", 12))
        self.command_label.pack()
        

        # periodically poll the queue for new snapshots
        self.root.after(50, self._process_queue)

    # ---- Public API ----
    def run(self):
        """Start the Tkinter mainloop (call from the main thread)."""
        self.root.mainloop()

    # ---- Blackboard Observer interface ----
    def update(self, data: Dict[str, Any]) -> None:
        """
        Called by Blackboard from arbitrary threads.
        We CANNOT touch Tkinter here; just enqueue the snapshot.
        """
        self._queue.put(data)

    # ---- Internal methods ----
    def _process_queue(self):
        """
        Periodically called in the Tk thread to apply the most recent snapshot.
        """
        latest = None
        while not self._queue.empty():
            latest = self._queue.get()

        if latest is not None:
            self._update_gui_from_snapshot(latest)

        # schedule next check
        self.root.after(50, self._process_queue)

    def _update_gui_from_snapshot(self, snapshot: Dict[str, Any]):
        """
        Read current_fixation and current_command from snapshot
        and update the canvas + labels.
        """
        changed = snapshot.get("changed")
        gaze = snapshot.get("current_gaze")
        fixation = snapshot.get("current_fixation")
        command = snapshot.get("current_command")
        print(snapshot)

        # ---- Extract gaze direction ----
        # Adjust this logic to match your actual FixationEvent / Command classes

        direction = None

        # Try to get from fixation first (e.g., fixation.direction)
        if fixation is not None:
            x, y = fixation.mean_x, fixation.mean_y
            self._draw_marker(x, y, "blue")
            self.fixation_label.config(text= f"Fixation around ({x:.2f}, {y:.2f})")
        else:
            self.fixation_label.config(text="Fixation around: (unknown)")


        # ---- Update marker position if we have a direction ----
        if gaze is not None:
            x, y = gaze.x, gaze.y
            self._draw_marker(x, y, "red")
            self.gaze_label.config(text=f"Last gaze: ({x:.2f}, {y:.2f})")
        else:
            # Unknown direction
            self.gaze_label.config(text="Last gaze: (unknown)")

        # ---- Update command label ----
        if command is not None:
            # Try to make a readable string from RobotCommand
            command_type = getattr(command, "command_type", None)
            cmd_name = getattr(command_type, "name", None) if command_type is not None else None
            if cmd_name:
                self.command_label.config(text=f"Last command: {cmd_name}")
            else:
                self.command_label.config(text=f"Last command: {command}")
        else:
            self.command_label.config(text="Last command: (none)")

    def _draw_marker(self, x: int, y: int, color: str):
        """Draw a small red circle at (x, y), removing the previous one."""
        if self.last_gaze_id is not None:
            self.canvas.delete(self.last_gaze_id)
        if self.last_fixation_id is not None:
            self.canvas.delete(self.last_fixation_id)

        px = x * self.width
        py = y * self.height
        r = max(8, int(self.width * 0.01))
        if color == "blue":
            self.last_fixation_id = self.canvas.create_oval(
                px - r, py - r, px + r, py + r,
                fill="blue"
            )
        elif color == "red":
            self.last_gaze_id = self.canvas.create_oval(
                px - r, py - r, px + r, py + r,
                fill="red"
            )
        else:   
            self.last_fixation_id = self.canvas.create_oval(
                px - r, py - r, px + r, py + r,
                fill="black"
            )
