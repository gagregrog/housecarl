import os
import cv2
import numpy as np

from library import constants
from library.video import RTSP

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

class MobileNetDetector:
    def __init__(self, config): 
        self.min_confidence = config['confidence']
        self.valid_classes = set(config['classes'])
        model_path =  os.path.join(constants.mobilenet_path, 'MobileNetSSD_deploy.caffemodel')
        prototxt_path =  os.path.join(constants.mobilenet_path, 'MobileNetSSD_deploy.prototxt')
        self.net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)


    def _class_is_valid(self, label):
        return label in self.valid_classes


    def _get_detections(self, frame):
        blob = cv2.dnn.blobFromImage(frame, size=(300, 300), ddepth=cv2.CV_8U)
        self.net.setInput(blob, scalefactor=1.0/127.5, mean=[127.5, 127.5, 127.5])
        detections = self.net.forward()

        return detections


    def _filter_detections(self, detections):
        filtered_detections = []

        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
 
            if confidence > self.min_confidence:
                class_idx = int(detections[0, 0, i, 1])
                label = CLASSES[class_idx]
                color = COLORS[class_idx]
 
                if not self._class_is_valid(label):
                    continue
                    
                filtered_detections.append((label, confidence, detections[0, 0, i, 3:7], color))

        return filtered_detections

    def detect(self, frame, debug=False):
        detections = self._get_detections(frame)
        detections = self._filter_detections(detections)
        (H, W) = frame.shape[:2]

        for (label, confidence, raw_box, color) in detections:
            box = raw_box * np.array([W, H, W, H])
            box = box.astype("int")
            formatted_detections = (label, confidence, box, color)
            
            if debug:
                print(formatted_detections)

            RTSP.draw_detection(frame, formatted_detections)

        return detections




