import time
from typing import List

from cv2.typing import MatLike
from typing_extensions import override

from autoui.color.Color import calculate_color_percentage
from autoui.feature.Box import Box
from autoui.scene.Scene import Scene
from autoui.task.FindFeatureTask import FindFeatureTask
from autoui.task.TaskExecutor import TaskExecutor
from genshin.scene.DialogScene import DialogScene

white_color = {
    'r': (240, 255),  # Red range
    'g': (240, 255),  # Green range
    'b': (240, 255)  # Blue range
}

dark_gray_color = {
    'r': (40, 60),  # Red range
    'g': (50, 75),  # Green range
    'b': (65, 85)  # Blue range
}


class AutoDialogTask(FindFeatureTask):
    dialog_vertical_distance = 0

    @override
    def run_frame(self, executor: TaskExecutor, scene: Scene, frame: MatLike):
        if isinstance(scene, DialogScene):
            if scene.button_play:
                # turn on autoplay
                print(f"AutoDialogTask:turn on auto play")
                self.interaction.left_click_box(scene.button_play)
                time.sleep(1)
            elif not self.try_find_click_dialog(frame):  # no dialog choices, we send space to speed up
                print(f"AutoDialogTask:found pause_button space")
                self.interaction.left_click()
                time.sleep(0.5)

    def try_find_click_dialog(self, frame):
        dialogs = self.find(frame, "button_dialog", 0.5, 0.5)
        if len(dialogs) > 0:  # try find dialog choices and click the first
            if len(dialogs) > 1:
                self.dialog_vertical_distance = abs(dialogs[0].y - dialogs[1].y)
                print(f"AutoDialogTask: dialog_vertical_distance {self.dialog_vertical_distance}")
            above_count = len(self.find_choices_above(frame, dialogs[0]))
            if above_count > 0:
                print(f"AutoDialogTask: Found {above_count} choices above dialog, won't click")
                return
            self.interaction.left_click_box(dialogs[0])
            time.sleep(1)
            return True

    def find_choices_above(self, frame, box) -> List[Box]:
        result = []
        if self.dialog_vertical_distance > 0:
            to_find = Box(box.x, box.y + self.dialog_vertical_distance, box.width, box.height)
            percentage_white = calculate_color_percentage(frame, to_find, white_color)
            percentage_grey = calculate_color_percentage(frame, to_find, dark_gray_color)
            print(
                f"AutoDialogTask: find_choices_above percentage_white {percentage_white} percentage_grey {percentage_grey}")
        return result
