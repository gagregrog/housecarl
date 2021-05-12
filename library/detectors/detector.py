import numpy as np

from library import utility
from library.video import RTSP

class Detector:
    def __init__(self, config):
        self.__verify_child()
        self._parse_config(config)
        self._set_valid_classes()
        self._set_colors()

    def __verify_child(self):
        if self.all_classes is None:
            raise Exception("Child of Detector must set self.all_classes")

    def _parse_config(self, config):
        self.config = config
        self.min_confidence = config['confidence']
        self.requested_classes = config['classes']

    def _set_valid_classes(self):
        self.valid_classes = utility.intersection(self.requested_classes, self.all_classes)

    def _set_colors(self):
        self.colors = np.random.uniform(0, 255, size=(len(self.valid_classes), 3))

    def class_is_valid(self, label):
        return label in self.valid_classes

    def get_class_index(self, label):
        return self.valid_classes.index(label)

    def get_label_color(self, label):
        return self.colors[self.get_class_index(label)]

    def filter_and_hydrate_normalized_detections(self, detections):
        filtered_detections = []

        for i, (class_index, confidence, box) in enumerate(detections):
            if confidence > self.min_confidence:
                label = self.all_classes[class_index]
                if self.class_is_valid(label):
                    color = self.get_label_color(label)
                    filtered_detections.append((label, confidence, box, color))

        return filtered_detections

    def get_valid_detections(self, frame):
        all_detections = self._get_normalized_detections(frame)
        detections = self.filter_and_hydrate_normalized_detections(all_detections)

        return detections

    def detect_and_draw(self, frame, debug=False):
        detections = self.get_valid_detections(frame)
        for detection in detections:
            if debug:
                print(detection)

            RTSP.draw_detection(frame, detection)



