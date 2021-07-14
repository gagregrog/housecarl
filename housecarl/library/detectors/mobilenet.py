import os
import cv2
import numpy as np

from housecarl.library import constants, utility
from housecarl.library.detectors.base_detector import BaseDetector

MOBILENET_CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]

class MobileNetDetector(BaseDetector):
    def __init__(self, config):
        self.__model_path = os.path.join(constants.mobilenet_path, 'MobileNetSSD_deploy.caffemodel')
        self.__prototxt_path = os.path.join(constants.mobilenet_path, 'MobileNetSSD_deploy.prototxt')
        
        self.config = config
        self.__set_all_classes()
        self.__read_net()
        
        super().__init__(config)

    def __set_all_classes(self):
        self.set_all_classes(MOBILENET_CLASSES)

    def __download_model_files(self):
        utility.ensure_dir(constants.mobilenet_path)

        # originally from https://www.pyimagesearch.com/2017/09/11/object-detection-with-deep-learning-and-opencv/
        model_url = 'https://drive.google.com/uc?export=download&id=1Im7t557U3eAajnKFSt5jD1HHKyuCBi0o'

        prototxt_url = 'https://drive.google.com/uc?export=download&id=1B0-S_Dd_tKljtMy-5-Yqn2biDrTVBZ3q'
        
        # we should parallelize this
        utility.download_file(model_url, self.__model_path)
        utility.download_file(prototxt_url, self.__prototxt_path)

    def __read_net(self):
        if not (os.path.exists(self.__model_path) and os.path.exists(self.__prototxt_path)):
            self.__download_model_files()

        self.__net = cv2.dnn.readNetFromCaffe(
            self.__prototxt_path,
            self.__model_path
        )

    def __get_raw_detections(self, frame):
        blob = cv2.dnn.blobFromImage(frame, size=(300, 300), ddepth=cv2.CV_8U)
        self.__net.setInput(blob, scalefactor=1.0/127.5, mean=[127.5, 127.5, 127.5])
        raw_detections = self.__net.forward()

        return raw_detections

    def __normalize_detections(self, raw_detections, frame):
        normalized_detections = []
        (H, W) = frame.shape[:2]

        for i in np.arange(0, raw_detections.shape[2]):
            confidence = raw_detections[0, 0, i, 2]
            class_idx = int(raw_detections[0, 0, i, 1])
            raw_box = raw_detections[0, 0, i, 3:7]
            float_box = raw_box * np.array([W, H, W, H])
            box = float_box.astype("int")
            normalized_detections.append((class_idx, confidence, box))

        return normalized_detections

    def _get_normalized_detections(self, frame):
        # must be provided to the BaseDetector
        raw_detections = self.__get_raw_detections(frame)
        normalized_detections = self.__normalize_detections(raw_detections, frame)

        return normalized_detections
