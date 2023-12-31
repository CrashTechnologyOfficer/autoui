#original https://github.com/Toufool/AutoSplit/blob/master/src/capture_method/WindowsGraphicsCaptureMethod.py
import asyncio
from typing import TYPE_CHECKING, cast
import pygetwindow

import numpy as np
from cv2.typing import MatLike
from typing_extensions import override
from win32 import win32gui
from math import ceil
from winsdk.windows.graphics import SizeInt32
from winsdk.windows.graphics.capture import Direct3D11CaptureFramePool, GraphicsCaptureSession
from winsdk.windows.graphics.capture.interop import create_for_window
from winsdk.windows.graphics.directx import DirectXPixelFormat
from winsdk.windows.graphics.imaging import BitmapBufferAccessMode, SoftwareBitmap

from capture.window import get_window_bounds
from capture.CaptureMethodBase import CaptureMethodBase
from capture.utils import BGRA_CHANNEL_COUNT, WGC_MIN_BUILD, WINDOWS_BUILD_NUMBER, get_direct3d_device, is_valid_hwnd

WGC_NO_BORDER_MIN_BUILD = 20348
LEARNING_MODE_DEVICE_BUILD = 17763
"""https://learn.microsoft.com/en-us/uwp/api/windows.ai.machinelearning.learningmodeldevice"""


class WindowsGraphicsCaptureMethod(CaptureMethodBase):
    name = "Windows Graphics Capture"
    short_description = "fast, most compatible, capped at 60fps"
    description = (
        f"\nOnly available in Windows 10.0.{WGC_MIN_BUILD} and up. "
        + f"\nDue to current technical limitations, Windows versions below 10.0.0.{LEARNING_MODE_DEVICE_BUILD}"
        + "\nrequire having at least one audio or video Capture Device connected and enabled."
        + "\nAllows recording UWP apps, Hardware Accelerated and Exclusive Fullscreen windows. "
        + "\nAdds a yellow border on Windows 10 (not on Windows 11)."
        + "\nCaps at around 60 FPS. "
    )

    size: SizeInt32
    frame_pool: Direct3D11CaptureFramePool | None = None
    session: GraphicsCaptureSession | None = None
    """This is stored to prevent session from being garbage collected"""
    last_captured_frame: MatLike | None = None
    hwnd = None

    def __init__(self, title = ""):
        super().__init__()
        self.title = title
        self.hwnd = win32gui.FindWindow(None, title)
        if not self.hwnd:
            print("window {title} not found")
            return

        item = create_for_window(self.hwnd)
        frame_pool = Direct3D11CaptureFramePool.create_free_threaded(
            get_direct3d_device(),
            DirectXPixelFormat.B8_G8_R8_A8_UINT_NORMALIZED,
            1,
            item.size,
        )
        if not frame_pool:
            raise OSError("Unable to create a frame pool for a capture session.")
        session = frame_pool.create_capture_session(item)
        if not session:
            raise OSError("Unable to create a capture session.")
        session.is_cursor_capture_enabled = False
        if WINDOWS_BUILD_NUMBER >= WGC_NO_BORDER_MIN_BUILD:
            session.is_border_required = False
        session.start_capture()

        self.session = session
        self.size = item.size
        self.frame_pool = frame_pool

    @override
    def close(self):
        if self.frame_pool:
            self.frame_pool.close()
            self.frame_pool = None
        if self.session:
            try:
                self.session.close()
            except OSError:
                # OSError: The application called an interface that was marshalled for a different thread
                # This still seems to close the session and prevent the following hard crash in LiveSplit
                # "AutoSplit.exe	<process started at 00:05:37.020 has terminated with 0xc0000409 (EXCEPTION_STACK_BUFFER_OVERRUN)>" # noqa: E501
                pass
            self.session = None

    def update_window_size(self):
        _, __, window_width, window_height = get_window_bounds(self.hwnd)
        _, __, client_width, client_height = win32gui.GetClientRect(self.hwnd)
        border_width = ceil((window_width - client_width) / 2)
        titlebar_with_border_height = window_height - client_height - border_width
        
        print(f"{window_width} {window_height} {client_width} {client_height}")
        self.x = 0#border_width
        self.y = 0#titlebar_with_border_height
        self.width = window_width#client_width
        self.height = window_height#client_height - border_width * 2
        
    @override
    def get_frame(self) -> tuple[MatLike | None, bool]:
        self.update_window_size()
        # We still need to check the hwnd because WGC will return a blank black image
        if not (
            self.check_selected_region_exists()
            # Only needed for the type-checker
            and self.frame_pool
        ):
            return None, False

        try:
            frame = self.frame_pool.try_get_next_frame()
        # Frame pool is closed
        except OSError:
            return None, False

        async def coroutine():
            # We were too fast and the next frame wasn't ready yet
            if not frame:
                return None
            return await (SoftwareBitmap.create_copy_from_surface_async(frame.surface) or asyncio.sleep(0, None))

        try:
            software_bitmap = asyncio.run(coroutine())
        except SystemError as exception:
            # HACK: can happen when closing the GraphicsCapturePicker
            if str(exception).endswith("returned a result with an error set"):
                return self.last_captured_frame, True
            raise

        if not software_bitmap:
            # HACK: Can happen when starting the region selector
            return self.last_captured_frame, True
            # raise ValueError("Unable to convert Direct3D11CaptureFrame to SoftwareBitmap.")
        bitmap_buffer = software_bitmap.lock_buffer(BitmapBufferAccessMode.READ_WRITE)
        if not bitmap_buffer:
            raise ValueError("Unable to obtain the BitmapBuffer from SoftwareBitmap.")
        reference = bitmap_buffer.create_reference()
        image = np.frombuffer(cast(bytes, reference), dtype=np.uint8)
        image.shape = (self.size.height, self.size.width, BGRA_CHANNEL_COUNT)
        image = image[
            self.y: self.y + self.height,
            self.x: self.x + self.width,
        ]
        self.last_captured_frame = image
        return image, False

    @override
    def recover_window(self, captured_window_title: str, autosplit: "AutoSplit"):
        hwnd = win32gui.FindWindow(None, captured_window_title)
        if not is_valid_hwnd(hwnd):
            return False
        autosplit.hwnd = hwnd
        try:
            self.reinitialize(autosplit)
        # Unrecordable hwnd found as the game is crashing
        except OSError as exception:
            if str(exception).endswith("The parameter is incorrect"):
                return False
            raise
        return self.check_selected_region_exists(autosplit)

    @override
    def check_selected_region_exists(self, ):
        return bool(
            is_valid_hwnd(self.hwnd)
            and self.frame_pool
            and self.session,
        )
    
    

# def get_window_by_title(title):
#     try:
#         window = pygetwindow.getWindowsWithTitle(title)[0]  # Get the first window with the given title
#         if window is not None:
#             return window._hWnd
#         else:
#             print("Window not found")
#             return None
#     except Exception as e:
#         print(f"Error: {e}")
#         return None