import os
import cv2
import numpy as np

from library import constants
from library.detectors.detector import Detector

class MobileNetDetector(Detector):
    def __init__(self, config):
        self._set_all_classes()
        self._read_net()
        
        super().__init__(config)

    def _set_all_classes(self):
        self.all_classes = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]

    def _read_net(self):
        model_path = os.path.join(constants.mobilenet_path, 'MobileNetSSD_deploy.caffemodel')
        prototxt_path = os.path.join(constants.mobilenet_path, 'MobileNetSSD_deploy.prototxt')
        self.net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

    def _get_raw_detections(self, frame):
        blob = cv2.dnn.blobFromImage(frame, size=(300, 300), ddepth=cv2.CV_8U)
        self.net.setInput(blob, scalefactor=1.0/127.5, mean=[127.5, 127.5, 127.5])
        raw_detections = self.net.forward()

        return raw_detections

    def _normalize_detections(self, raw_detections, frame):
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
        raw_detections = self._get_raw_detections(frame)
        normalized_detections = self._normalize_detections(raw_detections, frame)

        return normalized_detections
