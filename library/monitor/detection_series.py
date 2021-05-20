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
        self.num_frames_processed = 0
        self.num_detections_in_series = 0
        self._series_is_active = False
        self.best_confidence = None
        self.best_frame = None
        self.best_label = None

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
        num_processed = self.num_frames_processed
        if not num_processed or num_processed < self.min_detection_frames:
            return False

        detection_ratio = self.num_detections_in_series / num_processed

        return detection_ratio >= self.min_detection_ratio

    def detected_in_enough_frames(self):
        return self.num_detections_in_series >= self.min_detection_frames

    def should_activate_series(self):
        if self.series_is_active():
            return False

        processed_enough = self.detected_in_enough_frames()
        ratio_ok = self.detection_ratio_is_high_enough()

        return processed_enough and ratio_ok

    def series_is_activating(self):
        series_is_activating = self.should_activate_series()
        if series_is_activating:
            self.activate_series()

        return series_is_activating


    def series_is_active(self):
        return self._series_is_active

    def activate_series(self):
        self._series_is_active = True

    def process_frame(self, frame, detections):
        self.inc_detections()

        for (label, confidence, box, color) in detections:
            if not self.best_confidence or confidence > self.best_confidence:
                self.best_confidence = confidence
                self.best_frame = frame
                self.best_label = label

    def get_best_frame(self):
        return (self.best_frame, self.best_label, self.best_confidence)
