import cv2
import imutils
from time import sleep
from imutils.video import VideoStream, FPS

from library import utility

DEFAULT_SRC = 0
DEFAULT_VS_ARGS = (DEFAULT_SRC)

class Video:
    def __init__(
        self,
        config,
        frame_handler=None,
        on_exit=None,
        vs_args=DEFAULT_VS_ARGS,
        ):
        """
        Instantiate an object capable of managing a CV2 RTSP Video Stream.

        config is a required dict and must contain the following keys:
            show_video: bool
            frame_width: int
            rtsp_url: string

        vs_args is an optional tuple or dict that will be spread into the VideoStream constructor

        frame_handler is an optional function and is passed the following:
            frame: The current CV2 frame to be processed
            stop: A function that will terminate the loop

            If frame_handler has a function signature that accepts one argument, frame is passed.
            If frame_handler has a function signature that accepts two arguments, frame and then stop is passed.
            If frame_handler has a function signature that accepts any other number of arguments, an exception is raised.

        on_exit is an optional function that will be called when the video loop is closed
        """
        self.name = 'VideoStream'
        self.on_exit = on_exit
        self.frame_width = None
        self.show_video = False

        self.__fps = None
        self.__looping = False
        self.__pass_stop = False
        self.__verify_frame_handler(frame_handler)

        use_kwargs = type(vs_args).__name__ == 'dict'
        self.__vs = VideoStream(**vs_args) if use_kwargs else VideoStream(*vs_args)

        self._verify_config(config)

    def _verify_config(self, config):
        """
        Helper function to verify that config values are of the correct type and then set them on the instance.
        """
        
        # these are the types expected by Video
        expected_types = {
            'show_video': bool, 
            'frame_width': int, 
        }

        utility.process_expected_types(
            source=config,
            expected_types=expected_types,
            destination=self
        )    

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
                continue

            if self.frame_width:
                frame = imutils.resize(frame, width=self.frame_width)

            if self.frame_handler:
                self.__call_frame_handler(frame)

            self.__fps.update()
            print('SHOW_VIDEO: {}'.format(self.show_video))

            if self.show_video:
                cv2.imshow(self.name, frame)

                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    self.stop()
                    break

    def set_name(self, name):
        self.name = name
        return self

    def start(self):
        """
        Start the video stream and initiate the loop handler.
        """

        self.__vs.start()
        sleep(2)

        self.__fps = FPS().start()

        self.__run_loop()

        return self

    def stop(self):
        """
        Terminate the video loop and cleanup processes.
        """
        if not self.__looping:
            return

        self.__looping = False
        self.__fps.stop()
        print('Elapsed time: {:.2f}'.format(self.__fps.elapsed()))
        sleep(0.5)
        
        print('Approx FPS: {:.2f}'.format(self.__fps.fps()))
        cv2.waitKey(1)
        cv2.destroyAllWindows()
        self.__vs.stop()
        cv2.waitKey(1)
        
        if self.on_exit:
            self.on_exit()
