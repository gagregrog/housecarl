import cv2
import imutils
from time import sleep, time
from imutils.video import VideoStream, FPS

from housecarl.library.common import utility
from housecarl.library.setup import pi_camera
from housecarl.library.camera.read_video import ThreadedVideoReader

TIMEOUT = 60 # TODO: Make this configurable
DEFAULT_SRC = 0
DEFAULT_VS_ARGS = (DEFAULT_SRC)
class Video:
    def __init__(
        self,
        config,
        on_frame=None,
        on_exit=None,
        on_alert=None
    ):
        """
        Instantiate an object capable of managing a CV2 Video Source.

        config is a required CLI_Group and must contain the following keys:
            display: bool
            width: int
            src: string
            name: string

        on_frame is an optional function and is passed the following:
            frame: The current CV2 frame to be processed
            stop: A function that will terminate the loop

            If on_frame has a function signature that accepts one argument, frame is passed.
            If on_frame has a function signature that accepts two arguments, frame and then stop is passed.
            If on_frame has a function signature that accepts any other number of arguments, an exception is raised.

        on_exit is an optional function that will be called when the video loop is closed

        on_alert is an optional function that will be called with an alert message. Handle this however you see fit...like by sending a push notification.
        """
        self.__on_exit = on_exit
        self.__on_alert = on_alert

        self.config = config

        self.__fps = None
        self.__looping = False
        self.__pass_stop = False
        self.__frame_check_at = time()
        self.__broken_stream = False
        self.__verify_frame_handler(on_frame)

        # if src is a number like "0" coerce to an int
        try:
            src = int(self.config.get('src'))
            config.set('src', src)
        except Exception as e:
            print(str(e))

        if self.config.get('src') == 'usePiCamera':
            if not pi_camera.is_picamera_installed():
                pi_camera.setup_picamera()

            self.__vs = VideoStream(usePiCamera=True)
        else:
            self.__vs = ThreadedVideoReader(self.config.get('src'))

    def __verify_frame_handler(self, frame_handler):
        if frame_handler is not None:
            num_args_wanted = utility.num_args(frame_handler)
            
            if num_args_wanted < 1 or num_args_wanted > 2:
                raise Exception('frame_handler must accept (frame) or (frame, stop)')

            self.__pass_stop = num_args_wanted == 2

        self.__frame_handler = frame_handler

    def __call_frame_handler(self, frame):
        args = (frame, self.stop) if self.__pass_stop else (frame,)
        self.__frame_handler(*args)

    def __run_loop(self):
        """
        The mechanism to process video frames. Frame handler can initiate loop termination by calling stop()
        """

        self.__looping = True
        
        while self.__looping:
            frame = self.__vs.read()

            if frame is None:
                if time() - self.__frame_check_at > TIMEOUT:
                    # if we just detected a broken stream
                    if not self.__broken_stream:
                        self.__broken_stream = True

                        # only handle alert if the broken stream state is new
                        if self.__on_alert is not None:
                            self.__on_alert(
                                "No frames have been detected for {} seconds. Is the video stream working?".format(TIMEOUT)
                            )
                    # sleep when broken stream is first detected
                    sleep(30)

                    # reset the frame check time so have a chance to get more frames
                    self.__frame_check_at = time()

                continue
                
            self.__frame_check_at = time()

            # we've seen a frame again, so reset
            if self.__broken_stream:
                self.__broken_stream = False
                
                if self.__on_alert is not None:
                    self.__on_alert("Video stream detected again!")

            if self.config.get('width'):
                frame = imutils.resize(frame, width=int(self.config.get('width')))

            if self.__frame_handler:
                self.__call_frame_handler(frame)

            self.__fps.update()

            if self.config.get('display'):
                cv2.imshow(self.config.get('name'), frame)

                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    self.stop()
                    break

    def start(self):
        """
        Start the video stream and initiate the loop handler.
        """

        self.__vs.start()
        sleep(2)

        self.__fps = FPS().start()

        self.__run_loop()

    def stop(self):
        """
        Terminate the video loop and cleanup processes.
        """
        if not self.__looping:
            return

        self.__looping = False
        self.__fps.stop()
        utility.info('Elapsed time: {:.2f}'.format(self.__fps.elapsed()))
        sleep(0.5)
        
        utility.info('Approx FPS: {:.2f}\n'.format(self.__fps.fps()))
        cv2.waitKey(1)
        cv2.destroyAllWindows()
        self.__vs.stop()
        cv2.waitKey(1)
        
        if self.__on_exit:
            self.__on_exit()

    def get_fps(self):
        return 0 if not self.__fps else self.__fps.fps()
