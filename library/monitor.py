from time import time

from library import utility

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

    def add_frame(self, frame):
        self.frames.append(frame)

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

    def first_notification_was_sent(self):
        return self._sent_first_notification

    def send_first_notification(self):
        if self.first_notification_was_sent():
            return

        self._sent_first_notification = True
        # TODO: implement push notification

    def process_series(self):
        # TODO: implement series processing
        # save the video?
        # upload the video?
        pass

class Monitor:
    def __init__(self, config):
        self.debug = config['debug']
        self.config = config
        self.detection_series = None
        self.last_series_ended_at = None
        self.last_notification_sent_at = None

         # number of seconds to rest after a detection series
        self.post_detection_debounce = config['post_detection_debounce']

    def spawn_new_series(self):
        utility.info('Person detected! Spawing new detection series.')
        self.detection_series = DetectionSeries(self.config)

    def in_timeout(self):
        if self.detection_series:
            return False

        if not self.last_series_ended_at:
            time_ok = True
        else:
            time_since_last_series = time() - self.last_series_ended_at
            time_ok = time_since_last_series >= self.post_detection_debounce

        return not time_ok

    def handle_detections(self, detections, frame):
        # If we've recently ended a series, pause for a beat
        if self.in_timeout():
            return
            
        # there are detections and there is not currently a series
        if self.new_detection_series_needed(detections):
            self.spawn_new_series()

        # Nothing below applies if we're not in a series
        if not self.detection_series:
            return

        # add the frame irregardless of detections
        self.detection_series.add_frame(frame)

        if detections:
            self.detection_series.inc_detections()

        # perform all of the config['min'] checks
        if self.should_send_first_notification():
            self.send_first_notification()
            return

        max_life_reached = self.detection_series.max_life_reached()
        detection_lapse_exceeded = self.detection_series.detection_lapse_interval_exceeded()

        if max_life_reached or detection_lapse_exceeded:
            if detection_lapse_exceeded:
                utility.info('No detections for {} seconds'.format(self.config['detection_lapse_timeout']))
            else:
                utility.info('Max life of {} seconds reached'.format(self.config['max_detection_duration']))

            self.terminate_detection_series()

    def send_first_notification(self):
        self.last_notification_sent_at = time()
        self.detection_series.send_first_notification()
        utility.info('Person verified. Sending push notification!')


    def should_send_first_notification(self):
        if self.detection_series.first_notification_was_sent():
            return False

        duration_ok = self.detection_series.detection_duration_is_long_enough()
        ratio_ok = self.detection_series.detection_ratio_is_high_enough()

        return duration_ok and ratio_ok


    def terminate_detection_series(self):
        # we can assume the detection threshold was met,
        # otherwise we wouldn't have sent a notification
        if self.detection_series.first_notification_was_sent():
            self.last_series_ended_at = time()
            self.detection_series.process_series()
            utility.info('Processing detection series...')
            utility.info('Waiting {} seconds before starting new detection series.\n'.format(self.config['post_detection_debounce']))
        
        self.detection_series = None

    def new_detection_series_needed(self, detections):
        return detections and not self.detection_series
