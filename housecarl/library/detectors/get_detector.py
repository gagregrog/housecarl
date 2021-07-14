from housecarl.library.detectors.yolo import YoloDetector
from housecarl.library.detectors.mobilenet import MobileNetDetector
from housecarl.library.detectors.coral import CoralDetector

def Detector(config):
    model = config.get('model')

    if model == 'mobilenet':
        return MobileNetDetector(config)
    elif model == 'yolo':
        return YoloDetector(config)
    elif model == 'coral':
        return CoralDetector(config)

    raise Exception('config.detector.model must be one of ["mobilenet", "yolo", "coral"].')
