from time import sleep

from library import utility
from library.cli import CLI
from library.monitor import Monitor
from library.notifier import Pushover
from library.detectors import Detector
from library.camera import Video, Writer

def __main(video):
    cli = CLI().process()
    cli.print_config()
    pause = 3
    utility.info('Starting in {} seconds'.format(pause))

    # brief pause to read config
    sleep(pause)

    writer = None
    monitor = None
    detector = None
    pushover = None
    handle_frame = None

    writer_config = cli.get_writer_config()
    monitor_config = cli.get_monitor_config()
    detector_config = cli.get_detector_config()
    pushover_config = cli.get_pushover_config()

    if detector_config:
        utility.info('Loading detector...\n')
        detector = Detector(detector_config)

    if pushover_config:
        pushover = Pushover(pushover_config)

    if writer_config:
        writer = Writer(writer_config)

    if monitor_config:
        monitor = Monitor(
            config=monitor_config,
            writer=writer,
            pushover=pushover
        )

    if detector:
        handle_detections = None if not monitor else monitor.handle_detections
        
        handle_frame = lambda frame: detector.process_frame(
            frame,
            on_detections=handle_detections
        )

    def handle_exit():
        if monitor:
            monitor.finish_recording()

        if detector:
            detector.terminate_thread()

    # video is always required
    video = Video(
        config=cli.get_video_config(),
        on_frame=handle_frame,
        on_exit=handle_exit,
    )

    utility.info('Starting video stream...')
    video.start()

def carl():
    video = None

    try:
        __main(video)
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

if __name__ == "__main__":
    carl()