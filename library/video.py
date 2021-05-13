import cv2
import imutils
from time import sleep
from imutils.video import VideoStream, FPS

from library import utility

class RTSP:
    def __init__(self, config, frame_handler=None, on_exit=None):
        """
        Instantiate an object capable of managing a CV2 RTSP Video Stream.

        config is a required dict and must contain the following keys:
            frame_width: int
            show_video: bool
            rtsp_url: string

        frame_handler is an optional function and is passed the following:
            frame: The current CV2 frame to be processed
            stop: A function that will terminate the loop

            If frame_handler has a function signature that accepts one argument, frame is passed.
            If frame_handler has a function signature that accepts two arguments, frame and then stop is passed.
            If frame_handler has a function signature that accepts any other number of arguments, an exception is raised.

        on_exit is an optional function that will be called when the video loop is closed
        """

        self.fps = None
        self.writer = None
        self.looping = False
        self.rtsp_url = None
        self.show_video = False
        self.on_exit = on_exit
        self.frame_width = None
        self._verify_config(config)
        self.frame_handler = frame_handler
        self.vs = VideoStream(self.rtsp_url)
        self._process_frame_handler()


    def _process_frame_handler(self):
        """
        Helper function to determine the number of arguments expected by the provided frame_handler.
        """

        if not self.frame_handler:
            return

        handler_args = utility.num_args(self.frame_handler)

        if handler_args < 1 or handler_args > 2:
            raise Exception('frame_handler must accept one or two arguments')
        
        self.handler_args = handler_args
    

    def _verify_config(self, config):
        """
        Helper function to verify that config values are of the correct type.
        """
        
        expected_types = {
            'rtsp_url': str,
            'frame_width': int, 
            'show_video': bool, 
        }

        for (key, expected_type) in expected_types.items():
            value = config.get(key)

            if not value:
                raise Exception('Expected config["{}"] but found None.'.format(key))

            if not isinstance(value, expected_type):
                raise Exception('Expected config["{}"] to be an instance of {} but found {}'.format(key, str(expected_type), str(type(value))))

            setattr(self, key, value)
    

    def _handle_loop(self):
        """
        The mechanism to process video frames. Frame handler can initiate loop termination by 
        """

        self.looping = True
        
        while self.looping:
            frame = self.vs.read()

            if frame is None:
                continue

            if self.frame_width:
                frame = imutils.resize(frame, width=self.frame_width)

            if self.frame_handler:
                if self.handler_args == 1:
                    self.frame_handler(frame)
                else:
                    self.frame_handler(frame, self.stop)

            self.fps.update()

            if self.show_video:
                cv2.imshow('WyzeCam', frame)

                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    self.stop()
                    break


    def start(self):
        """
        Start the video stream and initiate the loop handler.
        """

        self.vs.start()
        sleep(2)
        self.fps = FPS().start()

        self._handle_loop()

        return self

    def stop(self):
        """
        Terminate the video loop and cleanup processes.
        """
        
        self.looping = False
        self.fps.stop()
        print('Elapsed time: {:.2f}'.format(self.fps.elapsed()))
        print('Approx FPS: {:.2f}'.format(self.fps.fps()))
        cv2.waitKey(1)
        cv2.destroyAllWindows()
        self.vs.stop()
        sleep(0.5)
        cv2.waitKey(1)
        
        if self.on_exit:
            self.on_exit()
    
    @staticmethod
    def draw_detection(frame, detections):
        (label, confidence, box, color) = detections

        text = '{}: {:.2f}'.format(label, confidence)

        cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), color, 2)

        x, y = box[:2]

        if y - 10 > 0:
            Y = y - 10
            X = x
        else:
            Y = y + 10
            X = x + 10

        cv2.putText(frame, label, (X, Y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, color, 2)

