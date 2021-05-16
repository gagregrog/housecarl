from time import time

class DetectionSeries:
    def __init__(self, config):
        self.debug = config['debug']

        # number of seconds of no detections to consider a detection series over
        self.detection_lapse_timeout = config['detection_lapse_timeout']

        # ratio of detections/frames to consider it a real detection
        self.min_detection_ratio = config['min_detection_ratio']
        
        # min amount of time before notifying that a detection has occurred
        self.min_detection_duration = config['min_detection_duration']
        
        # max amount of time before terminating the series
        self.max_detection_duration = config['max_detection_duration']

        now = time()
        self.first_detection_at = now
        self.last_detection_at = now
        self.frames = []
        self.num_detections_in_series = 0
        self._sent_first_notification = False

    def add_frame(self, frame, detections):
        self.frames.append((frame, detections))

    def inc_detections(self):
        self.num_detections_in_series += 1
        self.last_detection_at = time()

    def max_life_reached(self):
        time_since_first_detection = time() - self.first_detection_at

        return time_since_first_detection >= self.max_detection_duration

    def detection_lapse_interval_exceeded(self):
        time_since_last_detection = time() - self.last_detection_at

        return time_since_last_detection >= self.detection_lapse_timeout

    def detection_ratio_is_high_enough(self):
        detection_ratio = self.num_detections_in_series / len(self.frames)

        return detection_ratio >= self.min_detection_ratio

    def detection_duration_is_long_enough(self):
        duration = time() - self.first_detection_at

        return duration >= self.min_detection_duration

    def should_send_first_notification(self):
        if self.first_notification_was_sent():
            return False

        duration_ok = self.detection_duration_is_long_enough()
        ratio_ok = self.detection_ratio_is_high_enough()

        return duration_ok and ratio_ok

    def first_notification_was_sent(self):
        return self._sent_first_notification

    def mark_first_notification_sent(self):
        self._sent_first_notification = True

    def get_best_frame(self):
        best_frame = None
        highest_detection = None

        for (frame, detections) in self.frames:
            for (label, confidence, box, color) in detections:
                if not highest_detection or confidence > highest_detection:
                    highest_detection = confidence
                    best_frame = frame

        return best_frame

    def process_series(self):
        # TODO: implement series processing
        # save the video?
        # upload the video?
        pass
