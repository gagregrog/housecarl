import os
import cv2
import time
from queue import Queue
from pathlib import Path
from threading import Thread
from collections import deque
from datetime import datetime

from library import utility, constants

# https://www.pyimagesearch.com/2016/02/29/saving-key-event-video-clips-with-opencv/
class Writer:
    def __init__(self, config) -> None:
        utility.set_properties(config, self)
        self.out_dir = constants.recordings_path if self.out_dir == '' else os.path.abspath(os.path.expanduser(self.out_dir))

        self.__Q = None
        self.__writer = None
        self.__thread = None
        self.__recording = False
        self.__last_recording_path = None
        self.__frames = deque(maxlen=self.buffer_size)
        self.__fourcc = cv2.VideoWriter_fourcc(*self.fourcc)
        
    def __start(self, output_path):
        self.__recording = True
        (frame_height, frame_width) = self.__frames[0].shape[:2]
        dimensions = (frame_width, frame_height)
        self.__writer = cv2.VideoWriter(output_path, self.__fourcc, self.fps, dimensions, True)
        self.__Q = Queue()

        # add all frames in the deque to the queue
        [self.__Q.put(self.__frames[i - 1]) for i in range(len(self.__frames), 0, -1)]

        # start a thread to write frames to the vide file
        self.__thread = Thread(target=self.__write, args=())
        self.__thread.daemon = True
        self.__thread.start()

    def __write(self):
        while True:
            # terminate the thread when we are no longer recording
            if not self.__recording:
                return

            # if we have frames in the queue, write them
            if not self.__Q.empty():
                frame = self.__Q.get()
                self.__writer.write(frame)
            else:
                # if we have no frames to write, sleep so we don't waste CPU cycles
                time.sleep(self.timeout)

    def __flush(self):
        # write all remaining frames to the file
        while not self.__Q.empty():
            frame = self.__Q.get()
            self.__writer.write(frame)

    def is_recording(self):
        return self.__recording

    def start(self):
        free_disk_space = utility.get_free_space()
        if free_disk_space < self.min_disk_space:
            utility.error('Remaining disk space is too small to record video: {} < {}'.format(free_disk_space, self.min_disk_space))
            return

        if not self.is_recording():
            timestamp = datetime.now()
            date = timestamp.strftime("%Y-%m-%d")
            time = timestamp.strftime("%Hh%Mm%Ss")
            date_dir = os.path.join(self.out_dir, date)
            utility.ensure_dir(date_dir)
            filename = '{}_{}.avi'.format(date, time)
            filepath = os.path.join(date_dir, filename)
            self.__last_recording_path = filepath
            self.__start(filepath)

    def update(self, frame):
        # update the frames buffer
        self.__frames.appendleft(frame)

        # if we're recording, put the frame in the queue
        if self.__recording:
            self.__Q.put(frame)

    def finish(self):
        self.__recording = False
        self.__thread.join()
        self.__flush()
        self.__writer.release()
        utility.info('Recording saved to {}'.format(self.__last_recording_path))
