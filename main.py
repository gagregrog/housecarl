from library import utility
from library.video import RTSP
from library.detectors import get_detector

def main():
    args = utility.get_args()
    config = utility.get_config(args.get('config'))
    utility.info('Loaded configuration:')
    utility.print_config(config)

    utility.info('Loading detector...')
    detector = get_detector(config)

    video = RTSP(config=config, frame_handler=lambda frame: detector.detect(frame))

    utility.info('Starting video stream...')
    video.start()

if __name__ == "__main__":
    main()
