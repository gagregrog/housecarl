from .mobilenet import MobileNetDetector

def get_detector(config):
    detector = config['detector']

    if detector == 'mobilenet':
        return MobileNetDetector(config)
    elif detector == 'yolo'
        raise Exception('"yolo" detector not yet implemented')

    raise Exception('model must be one of ["mobilenet"].')
