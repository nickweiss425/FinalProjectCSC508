import tkinter as tk
import queue
from typing import Any, Dict

from blackboard import Blackboard, Observer 


class GazeDisplay(Observer):
    """
    tkinter observer that displays:
      - the last gaze direction
      - the last robot command
    """

    def __init__(self):

        # queue for thread safe communication from Blackboard threads to Tk mainloop
        self._queue: "queue.Queue[Dict[str, Any]]" = queue.Queue()

        # tkinter setup
        self.root = tk.Tk()
        self.root.title("Gaze & Command Display")

        # make window full monitor, no title bar
        self.root.attributes('-fullscreen', True)
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        # store screen center
        self.center_x = self.width // 2
        self.center_y = self.height // 2

        # set up grid layout on root window
        self.root.rowconfigure(0, weight=1)   
        self.root.rowconfigure(1, weight=0)   
        self.root.columnconfigure(0, weight=1)

        # create canvas, put in row 0, column 0 of grid
        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg="white"
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        

        # create diagonal lines
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


        # keep track of the last marker so we can remove it
        self.last_gaze_id = None
        self.last_fixation_id = None

        # create container below the canvas
        bottom_frame = tk.Frame(self.root)
        bottom_frame.grid(row=1, column=0, sticky="ew")
        bottom_frame.columnconfigure(0, weight=1)

        # info labels below canvas
        self.gaze_label = tk.Label(bottom_frame, text="Last gaze: (none)", font=("Arial", 12))
        self.gaze_label.pack()

        self.fixation_label = tk.Label(bottom_frame, text="Fixation around: (none)", font=("Arial", 12))
        self.fixation_label.pack()

        self.command_label = tk.Label(bottom_frame, text="Last command: (none)", font=("Arial", 12))
        self.command_label.pack()
        
        # periodically poll the queue for new snapshots
        self.root.after(50, self._process_queue)


    def run(self):
        """start the Tkinter mainloop"""
        self.root.mainloop()

    # ---- Blackboard Observer interface ----
    def update(self, data: Dict[str, Any]) -> None:
        """
        called by Blackboard .
        """
        # add data to queue
        self._queue.put(data)

    # ---- Internal methods ----
    def _process_queue(self):
        """
        periodically called in the Tk thread to apply the most recent snapshot
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
        and update the canvas + labels
        """

        changed = snapshot.get("changed")
        gaze = snapshot.get("current_gaze")
        fixation = snapshot.get("current_fixation")
        command = snapshot.get("current_command")
        print(snapshot)


        # draw new fixations
        if fixation is not None:
            x, y = fixation.mean_x, fixation.mean_y
            self._draw_marker(x, y, "blue")
            self.fixation_label.config(text= f"Fixation around ({x:.2f}, {y:.2f})")
        else:
            self.fixation_label.config(text="Fixation around: (unknown)")


        # update gaze position
        if gaze is not None:
            x, y = gaze.x, gaze.y
            self._draw_marker(x, y, "red")
            self.gaze_label.config(text=f"Last gaze: ({x:.2f}, {y:.2f})")
        else:
            self.gaze_label.config(text="Last gaze: (unknown)")

        # update command label
        if command is not None:
            # make readable string from robot command
            command_type = getattr(command, "command_type", None)
            cmd_name = getattr(command_type, "name", None) if command_type is not None else None
            if cmd_name:
                self.command_label.config(text=f"Last command: {cmd_name}")
            else:
                self.command_label.config(text=f"Last command: {command}")
        else:
            self.command_label.config(text="Last command: (none)")




    def _draw_marker(self, x: int, y: int, color: str):
        """draw a small circle at (x, y), removing the previous one"""
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
