from library.detectors.yolo import YoloDetector
from library.detectors.mobilenet import MobileNetDetector

def get_detector(config):
    model = config['model']

    if model == 'mobilenet':
        return MobileNetDetector(config)
    elif model == 'yolo':
        return YoloDetector(config)

    raise Exception('config.detector.model must be one of ["mobilenet", "yolo"].')
