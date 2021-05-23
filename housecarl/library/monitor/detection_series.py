from time import time

from housecarl.library import utility

class DetectionSeries:
    def __init__(self, config):
        utility.set_properties(config, self)

        now = time()
        self.__first_detection_at = now
        self.__last_detection_at = now
        self.__num_frames_processed = 0
        self.__num_detections_in_series = 0
        self.__series_is_active = False
        self.__best_confidence = None
        self.__best_frame = None
        self.__best_label = None

    def __inc_detections(self):
        self.__num_detections_in_series += 1
        self.__last_detection_at = time()

    def __detection_ratio_is_high_enough(self):
        num_processed = self.__num_frames_processed
        if not num_processed or num_processed < self.min_detection_frames:
            return False

        detection_ratio = self.__num_detections_in_series / num_processed

        return detection_ratio >= self.min_detection_ratio

    def __detected_in_enough_frames(self):
        return self.__num_detections_in_series >= self.min_detection_frames

    def __should_activate_series(self):
        if self.series_is_active():
            return False

        processed_enough = self.__detected_in_enough_frames()
        ratio_ok = self.__detection_ratio_is_high_enough()

        return processed_enough and ratio_ok


    def __activate_series(self):
        self.__series_is_active = True

    def series_is_activating(self):
        series_is_activating = self.__should_activate_series()
        if series_is_activating:
            self.__activate_series()

        return series_is_activating

    def series_is_active(self):
        return self.__series_is_active

    def inc_frames_processed(self):
        self.__num_frames_processed += 1

    def max_life_reached(self):
        time_since_first_detection = time() - self.__first_detection_at

        return time_since_first_detection >= self.max_detection_duration

    def detection_lapse_interval_exceeded(self):
        time_since_last_detection = time() - self.__last_detection_at

        return time_since_last_detection >= self.detection_lapse_timeout

    def process_frame(self, frame, detections):
        self.__inc_detections()

        for (label, confidence, box, color) in detections:
            if not self.__best_confidence or confidence > self.__best_confidence:
                self.__best_confidence = confidence
                self.__best_frame = frame
                self.__best_label = label

    def get_best_frame_tuple(self):
        return (self.__best_frame, self.__best_label, self.__best_confidence)
