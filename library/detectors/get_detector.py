from .yolo import YoloDetector
from .mobilenet import MobileNetDetector

def get_detector(config):
    detector = config['detector']

    if detector == 'mobilenet':
        return MobileNetDetector(config)
    elif detector == 'yolo':
        return YoloDetector(config)

    raise Exception('model must be one of ["mobilenet", "yolo"].')
