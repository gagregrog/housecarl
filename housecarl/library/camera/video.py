import cv2
import imutils
from time import sleep, time
from imutils.video import VideoStream, FPS

from housecarl.library import utility
from housecarl.library.setup import pi_camera

TIMEOUT = 60 # TODO: Make this configurable
DEFAULT_SRC = 0
DEFAULT_VS_ARGS = (DEFAULT_SRC)
class Video:
    def __init__(
        self,
        config,
        on_frame=None,
        on_exit=None,
    ):
        """
        Instantiate an object capable of managing a CV2 Video Source.

        config is a required dict and must contain the following keys:
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
        """
        self.on_exit = on_exit

        utility.set_properties(config, self)

        self.__fps = None
        self.__looping = False
        self.__pass_stop = False
        self.__last_frame_at = time()
        self.__verify_frame_handler(on_frame)

        try:
            self.src = int(self.src)
        except Exception as e:
            pass

        usePiCamera = self.src == 'usePiCamera'

        if usePiCamera:
            kwargs = {'usePiCamera': True}
            if not pi_camera.is_picamera_installed():
                pi_camera.setup_picamera()
        else:
            kwargs = {'src': self.src}

        self.__vs = VideoStream(**kwargs)

    def __verify_frame_handler(self, frame_handler):
        if frame_handler is not None:
            num_args_wanted = utility.num_args(frame_handler)
            
            if num_args_wanted < 1 or num_args_wanted > 2:
                raise Exception('frame_handler must accept (frame) or (frame, stop)')

            self.__pass_stop = num_args_wanted == 2

        self.frame_handler = frame_handler

    def __call_frame_handler(self, frame):
        args = (frame, self.stop) if self.__pass_stop else (frame,)
        self.frame_handler(*args)

    def __run_loop(self):
        """
        The mechanism to process video frames. Frame handler can initiate loop termination by calling stop()
        """

        self.__looping = True
        
        while self.__looping:
            frame = self.__vs.read()
            if frame is None:
                
                if time() - self.__last_frame_at > TIMEOUT:
                    raise Exception('No frames for {} seconds. Likely no video feed.'.format(TIMEOUT))

                continue
                
            self.__last_frame_at = time()

            if self.width:
                frame = imutils.resize(frame, width=self.width)

            if self.frame_handler:
                self.__call_frame_handler(frame)

            self.__fps.update()

            if self.display:
                cv2.imshow(self.name, frame)

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
        
        if self.on_exit:
            self.on_exit()
