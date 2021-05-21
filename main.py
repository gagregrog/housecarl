from library import utility
from library.camera import Video
from library.monitor import Monitor
from library.detectors import get_detector

video = None

def main():
    global video
    args = utility.get_args()
    config = utility.get_config(args.get('config'))
    utility.info('Loaded configuration:')
    utility.print_config(config)

    utility.info('Loading detector...')
    detector = get_detector(config)

    monitor = Monitor(config)

    def handle_video_frame(frame):
        detector.process_frame(frame, on_detections=monitor.handle_detections)

    def cleanup():
        if monitor:
            monitor.finish_recording()

        if detector:
            detector.terminate_thread()

    vs_args = (config.get('rtsp_url'),)
    video = Video(
        config=config,
        frame_handler=handle_video_frame,
        on_exit=cleanup,
        vs_args=vs_args
    ).set_name('Wyze Cam')

    utility.info('Starting video stream...')
    video.start()

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, Exception) as exception:
        if video:
            video.stop()

        is_interrupt = type(exception).__name__ == 'KeyboardInterrupt'
        
        msg = 'Keyboard Interrupt' if is_interrupt else 'Unexpected Exception'
        print('\n\n\t{}: Shutting down gracefully\n\n'.format(msg))
 
        # show error stack if not user interrupt
        if not is_interrupt:
            # raise any other types of exceptions
            raise exception
