import numpy as np
from threading import Thread
from multiprocessing import Queue

from housecarl.library.common import utility
from housecarl.library.camera.image import draw_detection

class BaseDetector:
    def __init__(self, config):
        self.__config = config
        self.__verify_child()
        self._set_valid_classes()
        self._set_colors()

        if self.config.get('threaded'):
            self.__inputQueue = Queue(maxsize=1)
            self.__outputQueue = Queue(maxsize=1)

            self.__thread_active = True
            t = Thread(target=self._handle_input_queue, args=())
            t.daemon = True
            t.start()

            # use [] instead of None for identifiability
            self.__last_detections = []

    @staticmethod
    def alert_missing(cls):
        utility.warn('Requested class "{}" does not exist in set of all classes.'.format(cls))

    def __verify_child(self):
        if self.__all_classes is None:
            raise Exception("Child of BaseDetector must set self.set_all_classes")

    def _set_valid_classes(self):
        is_dict = utility.get_typename(self.__all_classes) == 'dict'
        model_classes = self.__all_classes if not is_dict else self.__all_classes.values()
        self.__valid_classes = utility.intersection(self.config.get('classes'), model_classes)

        # inform of any missing requested classes
        [BaseDetector.alert_missing(cls) for cls in self.config.get('classes') if cls not in self.__valid_classes]


    def _set_colors(self):
        self.__colors = np.random.uniform(0, 255, size=(len(self.__valid_classes), 3))

    def _handle_input_queue(self):
        while self.__thread_active:
            # check to see if there is a frame in the input queue
            if not self.__inputQueue.empty():
                # grab the frame, run the detection, and add it to the queue
                frame = self.__inputQueue.get()

                detections = self.get_valid_detections(frame)
                self.__outputQueue.put(detections)

    def _process_frame_in_thread(self, frame, on_detections=None):
        # only put in new frames when we are ready to process them
        if self.__inputQueue.empty():
            self.__inputQueue.put(frame)

        if not self.__outputQueue.empty():
            self.__last_detections = self.__outputQueue.get()

        if self.config.get('show_detections') and self.__last_detections:
            self.draw_detections(frame, self.__last_detections)
        
        if on_detections:
            args = (self.__last_detections) if utility.num_args(on_detections) == 1 else (self.__last_detections, frame)
            on_detections(*args)

    def _process_frame_without_thread(self, frame, on_detections=None):
        detections = self.get_valid_detections(frame)
        if self.config.get('show_detections'):
            self.draw_detections(frame, detections)
        
        if on_detections:
            args = (detections) if utility.num_args(on_detections) == 1 else (detections, frame)
            on_detections(*args)

    def set_all_classes(self, classes):
        self.__all_classes = classes

    def class_is_valid(self, label):
        return label in self.__valid_classes

    def get_class_index(self, label):
        return self.__valid_classes.index(label)

    def get_label_color(self, label):
        return self.__colors[self.get_class_index(label)]

    def filter_and_hydrate_normalized_detections(self, detections):
        filtered_detections = []

        for (class_index, confidence, box) in detections:
            if confidence > self.config.get('min_confidence'):
                label = self.__all_classes[class_index]
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
        self.__thread_active = False

    def process_frame(self, frame, on_detections=None):
        if self.config.get('threaded'):
            self._process_frame_in_thread(frame, on_detections)
        else:
            self._process_frame_without_thread(frame, on_detections)
