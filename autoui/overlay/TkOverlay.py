import threading
import time  # Import time module to track update times
import tkinter as tk
from typing import List

from autoui.capture.WindowsGraphicsCaptureMethod import BaseCaptureMethod
from autoui.feature.Box import Box
from autoui.overlay.BaseOverlay import BaseOverlay


class TkOverlay(BaseOverlay):
    dpi_scaling = 1
    lock = threading.Lock()

    def __init__(self, method: BaseCaptureMethod, close_event: threading.Event):
        super().__init__()
        self.canvas = None
        self.method = method
        self.uiDict = {}
        root = tk.Tk()
        self.root = root
        self.init_window()
        self.init_canvas()
        self.exit_event = close_event
        self.time_to_expire = 1
        method.add_window_change_listener(self)

    def init_window(self):
        self.root.title("TkOverlay")
        self.root.overrideredirect(True)
        self.root.attributes('-transparentcolor', self.root['bg'])
        self.root.wm_attributes("-topmost", True)

    def init_canvas(self):
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.place(relwidth=1, relheight=1)

    def draw_boxes(self, key: str, boxes: List[Box], outline: str):
        if self.exit_event and self.exit_event.is_set():
            return
        self.root.after(0, lambda: self.tk_draw_boxes(key, boxes, outline))

    def tk_draw_boxes(self, key: str, boxes: List[Box], outline: str):
        current_time = time.time()  # Get the current time
        with self.lock:  # Use the lock to ensure thread safety
            # Check and remove old UI elements
            if key in self.uiDict:
                # Identify old UI elements
                old_uis = [ui for ui, update_time in self.uiDict[key] if
                           current_time - update_time >= self.time_to_expire]
                # Remove old UI elements
                for ui in old_uis:
                    self.canvas.delete(ui)
                # Keep only recent UI elements
                self.uiDict[key] = [item for item in self.uiDict[key] if current_time - item[1] < self.time_to_expire]

            # If not present, initialize the list
            if key not in self.uiDict:
                self.uiDict[key] = []

            for ui in self.uiDict[key]:
                self.canvas.delete(ui[0])

            # Draw new boxes and record their creation time
            for box in boxes:
                rect = self.canvas.create_rectangle(
                    box.x / self.dpi_scaling, box.y / self.dpi_scaling,
                    (box.x + box.width) / self.dpi_scaling,
                    (box.y + box.height) / self.dpi_scaling,
                    outline=outline)
                text = self.canvas.create_text(
                    box.x / self.dpi_scaling, (box.y + box.width) / self.dpi_scaling, anchor="nw",
                    fill=outline, text=f"{key}_{round(box.confidence * 100)}", font=("Arial", 20))
                # Append the UI element and the current time to the uiDict
                self.uiDict[key].append([rect, current_time])
                self.uiDict[key].append([text, current_time])

    def window_changed(self, visible, x, y, border, title_height, window_width, window_height, scaling):
        self.dpi_scaling = scaling
        print(
            f"TkOverlay window_changed {round(window_width / self.dpi_scaling)}x{round(window_height / self.dpi_scaling)}+{round(x)}+{round((y + title_height / self.dpi_scaling))}")
        self.root.geometry(
            f"{round(window_width / self.dpi_scaling)}x{round(window_height / self.dpi_scaling)}+{round(x + border / self.dpi_scaling)}+{round((y + title_height / self.dpi_scaling))}")
        if visible:
            self.root.deiconify()
        else:
            self.root.withdraw()

    def start(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            # Handle what happens after Ctrl+C is presse
            print("TkinterCaught KeyboardInterrupt, exiting...")
            if self.exit_event:
                self.exit_event.set()
            self.root.destroy()
