import sys
from typing import List

from autoui.feature.Box import Box
from autoui.feature.FeatureSet import FeatureSet


class FeatureInteraction:

    def __init__(self, interaction, feature_set: FeatureSet):
        self.interaction = interaction
        self.feature_set = feature_set

    def find(self, frame, feature_name, horizontal_variance=0, vertical_variance=0, threshold=0.8) -> List[Box]:
        boxes = self.feature_set.find_feature(frame, feature_name, horizontal_variance, vertical_variance, threshold)
        # for box in boxes:
        # print(f'Box {feature_name} found at: x={box.x}, y={box.y}, width={box.width}, height={box.height}')
        if hasattr(self.interaction.overlay, "draw_boxes"):
            self.interaction.overlay.draw_boxes(feature_name, boxes, "red")
        return boxes

    def find_one(self, frame, feature_name, horizontal_variance=0, vertical_variance=0, threshold=0.8) -> Box:
        boxes = self.find(frame, feature_name, horizontal_variance, vertical_variance, threshold)
        if len(boxes) > 1:
            print(f"find_one:found {feature_name} too many {len(boxes)}", file=sys.stderr)
        if len(boxes) == 1:
            return boxes[0]

    def on_feature(self, boxes):
        pass
