from typing_extensions import override

from autohelper.task.FindFeatureTask import FindFeatureTask
from show_case_genshin.scene.DialogChoicesScene import DialogChoicesScene


class AutoChooseDialogTask(FindFeatureTask):
    dialog_vertical_distance = 0

    @override
    def run_frame(self):
        if self.is_scene(DialogChoicesScene):
            self.logger.info(f"AutoChooseDialogTask choose first option")
            self.click_box(self.scene.dialogs[0])
            self.sleep(1)
            return True
