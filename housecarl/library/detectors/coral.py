import os
import cv2
import numpy as np

from housecarl.library import constants, utility
from housecarl.library.detectors.base_detector import BaseDetector

try:
    from pycoral.adapters.common import input_size
    from pycoral.adapters.detect import get_objects
    from pycoral.utils.dataset import read_label_file
    from pycoral.utils.edgetpu import make_interpreter
    from pycoral.utils.edgetpu import run_inference
except Exception as e:
    pass

class CoralDetector(BaseDetector):
    def __init__(self, config):
        try:
            import pycoral
        except Exception as e:
            raise Exception("pycoral not found. Make sure you've followed the instructions to install pycoral for your system.\n\n See https://github.com/RobertMcReed/housecarl/blob/main/README.Coral.md for more help.")

        self.labels_path = os.path.join(constants.coral_path, 'coco_labels.txt')
        self.model_path = os.path.join(constants.coral_path, 'ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite')
        
        self.__set_all_classes()
        self.__init_interpreter()
        
        super().__init__(config)

    def __set_all_classes(self):
        if not (os.path.exists(self.model_path) and os.path.exists(self.labels_path)):
            self.__download_model_files()

        labels = read_label_file(self.labels_path)
        self.set_all_classes(labels)

    def __download_model_files(self):
        utility.ensure_dir(constants.coral_path)

        # originally from https://coral.ai/models/object-detection/

        label_url = 'https://github.com/google-coral/test_data/raw/master/coco_labels.txt'

        model_url = 'https://github.com/google-coral/test_data/raw/master/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite'
        
        # we should parallelize this
        if not os.path.exists(self.model_path):
            utility.download_file(model_url, self.model_path)

        if not os.path.exists(self.labels_path):
            utility.download_file(label_url, self.labels_path)

    def __init_interpreter(self):
        self.interpreter = make_interpreter(self.model_path)
        self.interpreter.allocate_tensors()
        self.inference_size = input_size(self.interpreter)


    def __get_raw_detections(self, frame):
        cv2_im_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2_im_rgb = cv2.resize(cv2_im_rgb, self.inference_size)
        run_inference(self.interpreter, cv2_im_rgb.tobytes())
        raw_detections = get_objects(self.interpreter, self.min_confidence)

        return raw_detections

    def __normalize_detections(self, raw_detections, frame):
        normalized_detections = []
        (H, W) = frame.shape[:2]

        scale_x = W / self.inference_size[0]
        scale_y = H / self.inference_size[1]

        for detection in raw_detections:
            bbox = detection.bbox.scale(scale_x, scale_y)
            confidence = detection.score
            class_idx = detection.id
            float_box = np.array([bbox.xmin, bbox.ymin, bbox.xmax, bbox.ymax])
            box = float_box.astype("int")
            normalized_detections.append((class_idx, confidence, box))

        return normalized_detections

    def _get_normalized_detections(self, frame):
        # must be provided to the BaseDetector
        raw_detections = self.__get_raw_detections(frame)
        normalized_detections = self.__normalize_detections(raw_detections, frame)

        return normalized_detections
