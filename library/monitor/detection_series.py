from time import time

class DetectionSeries:
    def __init__(self, config):
        self.debug = config['debug']

        # number of seconds of no detections to consider a detection series over
        self.detection_lapse_timeout = config['detection_lapse_timeout']

        # ratio of detections/frames to consider it a real detection
        self.min_detection_ratio = config['min_detection_ratio']
        
        # min amount of time before notifying that a detection has occurred
        self.min_detection_frames = config['min_detection_frames']
        
        # max amount of time before terminating the series
        self.max_detection_duration = config['max_detection_duration']

        now = time()
        self.first_detection_at = now
        self.last_detection_at = now
        self.frames = []
        self.num_frames_processed = 0
        self.num_detections_in_series = 0
        self._sent_first_notification = False

    def add_frame(self, frame, detections):
        self.frames.append((frame, detections))

    def inc_detections(self):
        self.num_detections_in_series += 1
        self.last_detection_at = time()

    def inc_frames_processed(self):
        self.num_frames_processed += 1

    def max_life_reached(self):
        time_since_first_detection = time() - self.first_detection_at

        return time_since_first_detection >= self.max_detection_duration

    def detection_lapse_interval_exceeded(self):
        time_since_last_detection = time() - self.last_detection_at

        return time_since_last_detection >= self.detection_lapse_timeout

    def detection_ratio_is_high_enough(self):
        detection_ratio = self.num_detections_in_series / len(self.frames)

        return detection_ratio >= self.min_detection_ratio

    def processed_enough_frames(self):
        return self.num_frames_processed >= self.min_detection_frames

    def should_send_first_notification(self):
        if self.first_notification_was_sent():
            return False

        processed_enough = self.processed_enough_frames()
        ratio_ok = self.detection_ratio_is_high_enough()

        return processed_enough and ratio_ok

    def first_notification_was_sent(self):
        return self._sent_first_notification

    def mark_first_notification_sent(self):
        self._sent_first_notification = True

    def get_best_frame(self):
        best_frame = None
        best_label = None
        best_confidence = None

        for (frame, detections) in self.frames:
            for (label, confidence, box, color) in detections:
                if not best_confidence or confidence > best_confidence:
                    best_confidence = confidence
                    best_frame = frame
                    best_label = label

        return (best_frame, best_label, best_confidence)

    def process_series(self):
        # TODO: implement series processing
        # save the video?
        # upload the video?
        pass
