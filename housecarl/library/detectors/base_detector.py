import numpy as np
from threading import Thread
from multiprocessing import Queue

from housecarl.library import utility
from housecarl.library.camera.image import draw_detection

class BaseDetector:
    def __init__(self, config):
        self.__verify_child()
        self._parse_config(config)
        self._set_valid_classes()
        self._set_colors()

        if self.threaded:
            self.inputQueue = Queue(maxsize=1)
            self.outputQueue = Queue(maxsize=1)

            self.thread_active = True
            t = Thread(target=self._handle_input_queue, args=())
            t.daemon = True
            t.start()

            # use [] instead of None for identifiability
            self.last_detections = []

    @staticmethod
    def alert_missing(cls):
        utility.warn('Requested class "{}" does not exist in set of all classes.'.format(cls))

    def __verify_child(self):
        if self.all_classes is None:
            raise Exception("Child of BaseDetector must set self.all_classes")

    def _parse_config(self, config):
        # this sets all of the properties from the config so they are accessible by the class instance
        utility.set_properties(config, self)

    def _set_valid_classes(self):
        is_dict = utility.get_typename(self.all_classes) == 'dict'
        model_classes = self.all_classes if not is_dict else self.all_classes.values()
        self.valid_classes = utility.intersection(self.classes, model_classes)

        # inform of any missing requested classes
        [BaseDetector.alert_missing(cls) for cls in self.classes if cls not in self.valid_classes]


    def _set_colors(self):
        self.colors = np.random.uniform(0, 255, size=(len(self.valid_classes), 3))

    def _handle_input_queue(self):
        while self.thread_active:
            # check to see if there is a frame in the input queue
            if not self.inputQueue.empty():
                # grab the frame, run the detection, and add it to the queue
                frame = self.inputQueue.get()

                detections = self.get_valid_detections(frame)
                self.outputQueue.put(detections)

    def _process_frame_in_thread(self, frame, on_detections=None):
        # only put in new frames when we are ready to process them
        if self.inputQueue.empty():
            self.inputQueue.put(frame)

        if not self.outputQueue.empty():
            self.last_detections = self.outputQueue.get()

        if self.show_detections and self.last_detections:
            self.draw_detections(frame, self.last_detections)
        
        if on_detections:
            args = (self.last_detections) if utility.num_args(on_detections) == 1 else (self.last_detections, frame)
            on_detections(*args)

    def _process_frame_without_thread(self, frame, on_detections=None):
        detections = self.get_valid_detections(frame)
        if self.show_detections:
            self.draw_detections(frame, detections)
        
        if on_detections:
            args = (detections) if utility.num_args(on_detections) == 1 else (detections, frame)
            on_detections(*args)

    def set_all_classes(self, classes):
        self.all_classes = classes

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

        return filtered_detections

    def get_valid_detections(self, frame):
        # self._get_normalized_detections must be provided by the inheriting class
        detections = None

        try:
            all_detections = self._get_normalized_detections(frame)
            detections = self.filter_and_hydrate_normalized_detections(all_detections)
        except Exception as e:
            utility.error('error running inference\n', e)
        # return [] instead of None so we can determine
        # if the detections are new or old (threaded)
        return detections if detections else []

    def draw_detections(self, frame, detections):
        for detection in detections:
            draw_detection(frame, detection)

    def detect_and_draw(self, frame):
        detections = self.get_valid_detections(frame)
        self.draw_detections(frame, detections)

    def terminate_thread(self):
        self.thread_active = False

    def process_frame(self, frame, on_detections=None):
        if self.threaded:
            self._process_frame_in_thread(frame, on_detections)
        else:
            self._process_frame_without_thread(frame, on_detections)
