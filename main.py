from library import utility
from library.video import RTSP
from library.monitor import Monitor
from library.detectors import get_detector

def main():
    args = utility.get_args()
    config = utility.get_config(args.get('config'))
    utility.info('Loaded configuration:')
    utility.print_config(config)

    utility.info('Loading detector...')
    detector = get_detector(config)

    monitor = Monitor(config)

    def handle_video_frame(frame):
        detector.process_frame(frame, on_detections=monitor.handle_detections)

    video = RTSP(
        config=config,
        frame_handler=handle_video_frame,
        on_exit=detector.terminate_thread
    )

    utility.info('Starting video stream...')
    video.start()

if __name__ == "__main__":
    main()
