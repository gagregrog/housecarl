from time import sleep

from library import utility
from library.cli import CLI
from library.monitor import Monitor
from library.notifier import Pushover
from library.detectors import Detector
from library.camera import Video, Writer

video = None

def main():
    global video
    cli = CLI().process()
    cli.print_config()
    pause = 3
    utility.info('Starting in {} seconds'.format(pause))
    # brief pause to read config
    sleep(pause)

    utility.info('Loading detector...')
    detector = Detector(cli.get_detector_config())

    pushover = None
    pushover_config = cli.get_pushover_config()
    if pushover_config:
        pushover = Pushover(pushover_config)

    writer = None
    writer_config = cli.get_writer_config()
    if writer_config:
        writer = Writer(writer_config)

    monitor = Monitor(
        config=cli.get_monitor_config(),
        writer=writer,
        pushover=pushover
    )

    def handle_video_frame(frame):
        detector.process_frame(
            frame,
            on_detections=monitor.handle_detections
        )

    def cleanup():
        if monitor:
            monitor.finish_recording()

        if detector:
            detector.terminate_thread()

    video = Video(
        config=cli.get_video_config(),
        frame_handler=handle_video_frame,
        on_exit=cleanup,
    )

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
