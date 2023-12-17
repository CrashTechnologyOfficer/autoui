import threading
import time
import cv2
from autoui.capture.WindowsGraphicsCaptureMethod import CaptureMethodBase
from autoui.save.SaveMethodBase import SaveMethodBase
from pynput import keyboard, mouse
from autoui.save.PostProcessor import PostProcessor

class SaveByKeyPress(SaveMethodBase):

    def __init__(self, method : CaptureMethodBase, image_processor:PostProcessor = None, capture_key = "c", stop_key = "x"):
        super().__init__(method, image_processor) 
        self.capture_key = capture_key
        self.stop_key = stop_key
        listener = keyboard.Listener(on_release=self.on_key_release)
        listener.start()

    def on_key_release(self, key):
        print(f'Key {key} released')
        try:
            if key.char == self.capture_key:
                print(f'is capture_key call save()')
                self.save()
            elif key.char == self.stop_key:
                self.stop()
                return False
        except AttributeError as e:
            print(f'AttributeError {e} key {key} released')