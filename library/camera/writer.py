import os
import cv2
import time
from queue import Queue
from pathlib import Path
from threading import Thread
from collections import deque
from datetime import datetime

from library import utility

# https://www.pyimagesearch.com/2016/02/29/saving-key-event-video-clips-with-opencv/
class Writer:
    def __init__(self, config) -> None:
        self.min_disk_space = config.get('min_disk_space')
        self.buf_size = config.get('buffer_size') or 64
        self.timeout = config.get('timeout') or 1.0
        self.out_dir = os.path.abspath(os.path.expanduser(config['out_dir']))
        self.fps = config.get('fps') or 15
        fourcc = config.get('fourcc') or 'MJPG'
        self.fourcc = cv2.VideoWriter_fourcc(*fourcc)

        self.frames = deque(maxlen=self.buf_size)
        self.Q = None
        self.writer = None
        self.thread = None
        self.recording = False

    def is_recording(self):
        return self.recording

    def update(self, frame):
        # update the frames buffer
        self.frames.appendleft(frame)

        # if we're recording, put the frame in the queue
        if self.recording:
            self.Q.put(frame)

    def start_recording(self):
        free_disk_space = utility.get_free_space()
        if free_disk_space < self.min_disk_space:
            utility.warn('Remaining disk space is too small to record video: {} < {}'.format(free_disk_space, self.min_disk_space))
            return

        if not self.is_recording():
            timestamp = datetime.now()
            date = timestamp.strftime("%Y-%m-%d")
            time = timestamp.strftime("%H:%M:%S")
            date_dir = os.path.join(self.out_dir, date)
            Path(date_dir).mkdir(parents=True, exist_ok=True)
            filepath = os.path.join(date_dir, '{}.avi'.format(time))
            self.last_recording_path = filepath
            self.start(filepath, self.fourcc, self.fps)

        

    def start(self, output_path, fourcc, fps):
        self.recording = True
        (frame_height, frame_width) = self.frames[0].shape[:2]
        dimensions = (frame_width, frame_height)
        self.writer = cv2.VideoWriter(output_path, fourcc, fps, dimensions, True)
        self.Q = Queue()

        # add all frames in the deque to the queue
        [self.Q.put(self.frames[i - 1]) for i in range(len(self.frames), 0, -1)]

        # start a thread to write frames to the vide file
        self.thread = Thread(target=self.write, args=())
        self.thread.daemon = True
        self.thread.start()

    def write(self):
        while True:
            # terminate the thread when we are no longer recording
            if not self.recording:
                return

            # if we have frames in the queue, write them
            if not self.Q.empty():
                frame = self.Q.get()
                self.writer.write(frame)
            else:
                # if we have no frames to write, sleep so we don't waste CPU cycles
                time.sleep(self.timeout)

    def flush(self):
        # write all remaining frames to the file
        while not self.Q.empty():
            frame = self.Q.get()
            self.writer.write(frame)

    def finish(self):
        self.recording = False
        self.thread.join()
        self.flush()
        self.writer.release()
        utility.info('Recording saved to {}'.format(self.last_recording_path))
