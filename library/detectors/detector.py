import numpy as np
from threading import Thread
from multiprocessing import Queue

from library import utility
from library.video import RTSP

class Detector:
    def __init__(self, config):
        self.__verify_child()
        self._parse_config(config)
        self._set_valid_classes()
        self._set_colors()

        if self.threaded:
            self.inputQueue = Queue(maxsize=1)
            self.outputQueue = Queue(maxsize=1)

            t = Thread(target=self._handle_input_queue, args=())
            t.daemon = True
            t.start()
            self.last_detections = None

    def __verify_child(self):
        if self.all_classes is None:
            raise Exception("Child of Detector must set self.all_classes")

    def _parse_config(self, config):
        self.config = config
        self.min_confidence = config['min_confidence']
        self.requested_classes = config['classes']
        self.threaded = config['threaded']
        self.show_detections = config['show_detections']
        self.debug = config['debug']

    def set_all_classes(self, classes):
        self.all_classes = classes

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

        for (class_index, confidence, box) in detections:
            if confidence > self.min_confidence:
                label = self.all_classes[class_index]
                if self.class_is_valid(label):
                    color = self.get_label_color(label)
                    detection = (label, confidence, box, color)
                    filtered_detections.append(detection)
                    if self.debug:
                        print(detection)

        return filtered_detections

    def get_valid_detections(self, frame):
        all_detections = self._get_normalized_detections(frame)
        detections = self.filter_and_hydrate_normalized_detections(all_detections)

        return detections

    def draw_detections(self, frame, detections):
        for detection in detections:
            RTSP.draw_detection(frame, detection)

    def detect_and_draw(self, frame):
        detections = self.get_valid_detections(frame)
        self.draw_detections(frame, detections)

    def _handle_input_queue(self):
        while True:
            # check to see if there is a frame in the input queue
            if not self.inputQueue.empty():
                # grab the frame, run the detection, and add it to the queue
                frame = self.inputQueue.get()

                detections = self.get_valid_detections(frame)
                self.outputQueue.put(detections)

    def _process_frame_in_thread(self, frame):
        current_detections = None

        # only put in new frames when we are ready to process them
        if self.inputQueue.empty():
            self.inputQueue.put(frame)

        if not self.outputQueue.empty():
            current_detections = self.outputQueue.get()

        if current_detections is not None:
            self.last_detections = current_detections
            # will ultimately need to handle detections here 
            # possibly add to an accumulator or notifier class

        if self.show_detections and self.last_detections is not None:
            self.draw_detections(frame, self.last_detections)

    def process_frame(self, frame):
        if self.threaded:
            self._process_frame_in_thread(frame)
        else:
            self.detect_and_draw(frame)
