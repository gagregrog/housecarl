import cv2
import time
from threading import Thread
from collections import deque

from housecarl.library import utility

# https://stackoverflow.com/a/58599708/8643833
class ThreadedVideoReader:
    """
    Independent camera feed.
    
    Uses threading to grab video frames in the background.

    Supports webcam, usb cameras, ip cameras, RTSP streams, and video files.

    capturing the frames in a separate thread prevents decoding errors that crash RTSP streams.

    These errors may look like:
        [h264 @ 0x2087c50] error while decoding MB 43 37, bytestream -7
        [h264 @ 0x1915f60] cabac decode of qscale diff failed at 36 12
        [h264 @ 0x1915f60] error while decoding MB 36 12, bytestream 807

    @param src - IP/RTSP/Webcam source
    @param reconnect - Boolean, reconnect if disconnected (or video ends)
    """

    def __init__(self, src=0, reconnect=True):
        self.__src = src
        self.__reconnect = reconnect
        self.__looping = False

        # Initialize deque used to store frames read from the stream
        # maxlen=1 means we always reference the latest available frame
        self.__deque = deque(maxlen=1)

        # Flag to check if camera is valid/working
        self.__online = False
        self.__capture = None


    def __begin(self):
        if self.__looping:
            return

        self.__looping = True
        self.__load_video_source()

        # Start background frame grabbing
        self.__get_frame_thread = Thread(target=self.__get_frame_in_thread, args=())
        self.__get_frame_thread.daemon = True
        self.__get_frame_thread.start()


    def __verify_video_source(self):
        """Checks if the video source is available"""

        cap = cv2.VideoCapture(self.__src)

        if not cap.isOpened():
            return False

        cap.release()

        return True


    def __load_video_source(self):
        """Verifies video source and opens it if valid"""

        def load_video_in_thread():
            if self.__verify_video_source():
                self.__capture = cv2.VideoCapture(self.__src)
                self.__online = True
                utility.info('Connected to stream: {}'.format(self.__src))

        load_video_thread = Thread(target=load_video_in_thread, args=())
        load_video_thread.daemon = True
        load_video_thread.start()


    def __get_frame_in_thread(self):
        """Reads frame and inserts into the dequeue"""

        while self.__looping:
            try:
                if self.__capture.isOpened() and self.__online:
                    # Read next frame from stream
                    status, frame = self.__capture.read()

                    if status:
                        # if the frame is valid, replace the current frame in the queue with it
                        self.__deque.append(frame)
                    else:
                        # we need to reconnect to the camera next loop
                        self.__capture.release()
                        self.__online = False
                elif self.__reconnect:
                    # Attempt to reconnect
                    utility.info('Attempting to reconnect:', self.__src)
                    self.__load_video_source()
                    self.__spin(2)
                else:
                    print('BREAK')
                    break

                self.__spin(.001)
            except AttributeError:
                pass

        if self.__capture:
            self.__capture.release()
            self.__capture = None
            self.__looping = False
            self.__online = False


    def __spin(self, seconds):
        """Pause for set amount of seconds, replaces time.sleep so program doesn't stall"""

        time_end = time.time() + seconds
        while time.time() < time_end:
            pass


    def streaming(self):
        return self.__looping


    def start(self):
        self.__begin()

        return self


    def stop(self):
        self.__looping = False


    def read(self):
        """
        Get the latest frame if it exists
        """

        if not self.streaming():
            return None
        if not self.__online:
            self.__spin(1)
            return None

        if self.__deque and self.__online:
            # Grab latest frame
            # note this won't remove it from the queue,
            # but it will be overwritten the next time a new frame is available
            frame = self.__deque[-1]

            return frame
