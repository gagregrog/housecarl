from time import sleep

from housecarl.library import utility
from housecarl.library.cli import CLI
from housecarl.library.monitor import Monitor
from housecarl.library.notifier import Pushover
from housecarl.library.detectors import Detector
from housecarl.library.camera import Video, Writer
from housecarl.library.server.server import Server
from housecarl.library.setup.coral import setup_coral

def __main(video):
    cli = CLI().process()

    if cli.should_setup_coral():
        return setup_coral()
    
    cli.print_config()

    server = None
    writer = None
    monitor = None
    detector = None
    pushover = None
    handle_frame = None
    handle_alert = None

    server_config = cli.get_server_config()
    writer_config = cli.get_writer_config()
    monitor_config = cli.get_monitor_config()
    detector_config = cli.get_detector_config()
    pushover_config = cli.get_pushover_config()

    if detector_config:
        utility.info('Loading detector...\n')
        detector = Detector(detector_config)

    if pushover_config:
        pushover = Pushover(pushover_config)
        handle_alert = lambda message: pushover.send_push_notification(message)

    if writer_config:
        writer = Writer(writer_config)

    if monitor_config:
        monitor = Monitor(
            config=monitor_config,
            writer=writer,
            pushover=pushover
        )

    if server_config:
        server = Server(server_config)
        server.start()

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
        on_alert=handle_alert,
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


        is_coral = 'Failed to load delegate from libedgetpu' in str(exception)

        if is_coral:
            utility.info('Did you forget to plug in your Coral?\n\n')
            return

        # show error stack if not user interrupt
        if not is_interrupt:
            # raise any other types of exceptions
            raise exception

if __name__ == "__main__":
    carl()
