import os
import cv2
import numpy as np

from library import constants, utility
from library.detectors.base_detector import BaseDetector

# constants
SCALE = 1/255
NMS_THRESH = 0.4
CONF_THRESH = 0.5

# @article{yolov3,
#   title={YOLOv3: An Incremental Improvement},
#   author={Redmon, Joseph and Farhadi, Ali},
#   journal = {arXiv},
#   year={2018}
# }

class YoloDetector(BaseDetector):
    def __init__(self, config):
        self.__classes_path = os.path.join(constants.yolo_path, 'coco.names')
        self.__cfg_path = os.path.join(constants.yolo_path, 'yolov3.cfg')
        self.__weights_path = os.path.join(constants.yolo_path, 'yolov3.cfg')

        self._set_all_classes()
        self._read_net()

        super().__init__(config)

    def __download_model_files(self):
        classes_url = 'https://github.com/pjreddie/darknet/blob/master/data/coco.names'
        weights_url = 'https://pjreddie.com/media/files/yolov3.weights'
        cfg_url = 'https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg'

        utility.download_file(classes_url, self.__classes_path)
        utility.download_file(weights_url, self.__weights_path)
        utility.download_file(cfg_url, self.__cfg_path)

    def _set_all_classes(self):
        if not os.path.exists(self.__classes_path):
            self.__download_model_files()

        # read the class names from yolov3.txt
        with open(self.classesPath, 'r') as f:
            # self.set_all_classes is inherited
            self.set_all_classes([line.strip() for line in f.readlines()])

    def _read_net(self):
        # read the pretrained model and configs
        self.net = cv2.dnn.readNetFromDarknet(self.__cfg_path, self.__weights_path)

        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)


    def _get_raw_detections(self, frame):
        # create the input blob
        blob = cv2.dnn.blobFromImage(frame, SCALE, (416, 416), (0, 0, 0), True, crop=False)

        # set the input for the neural net
        self.net.setInput(blob)

        layer_names = self.net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

        # gather the predictions from the output layers
        raw_detections = self.net.forward(output_layers)

        return raw_detections

    def _normalize_detections(self, raw_detections, frame):
        normalized_detections = []

        (H, W) = frame.shape[:2]
        # initializations
        class_ids = []
        confs = []
        boxes = []

        # for each detection in each output layer,
        # get the confidence, class_id, bounding box params,
        
        for output_layer in raw_detections:
            for detection in output_layer:
                scores = detection[5:]
                class_id = np.argmax(scores)
                conf = scores[class_id]

                center_x = int(detection[0] * W)
                center_y = int(detection[1] * H)
                w = int(detection[2] * W)
                h = int(detection[3] * H)
                x = center_x - w / 2
                y = center_y - h / 2

                class_ids.append(class_id)
                confs.append(float(conf))
                boxes.append([x, y, w, h])

        # apply non-maxima suppression
        indices = cv2.dnn.NMSBoxes(boxes, confs, CONF_THRESH, NMS_THRESH)

        for i in indices:
            i = i[0]
            x, y, w, h = boxes[i][:4]
            class_id = class_ids[i]
            confidence = confs[i]
            box = [round(x), round(y), round(x + w), round(y + h)]
            normalized_detections.append((class_id, confidence, box))

        return normalized_detections

    def _get_normalized_detections(self, frame):
        # must be provided to the BaseDetector
        raw_detections = self._get_raw_detections(frame)
        normalized_detections = self._normalize_detections(raw_detections, frame)

        return normalized_detections
