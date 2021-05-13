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
        print('detection_ratio: {}'.format(detection_ratio))

        return detection_ratio >= self.min_detection_ratio

    def detection_duration_is_long_enough(self):
        duration = time() - self.first_detection_at
        print('detection_duration: {}'.format(duration))

        return duration >= self.min_detection_duration

    def first_notification_was_sent(self):
        return self._sent_first_notification

    def send_first_notification(self):
        if self.first_notification_was_sent():
            return

        self._sent_first_notification = True

        print('\nSending first notification:\n\tA PERSON HAS BEEN DETECTED!')
        # TODO: implement push notification

    def process_series(self):
        # TODO: implement series processing
        # save the video?
        # upload the video?
        print('\nPROCESSING DETECTION SERIES!')


class Monitor:
    def __init__(self, config):
        self.debug = config['debug']
        self.config = config
        self.detection_series = None
        self.last_notification_sent_at = None

         # minimum number of seconds between detection push notifications
        self.min_notification_interval = config['min_notification_interval']

    def spawn_new_series(self):
        self.detection_series = DetectionSeries(self.config)

    def handle_detections(self, detections, frame):
        if self.new_detection_series_needed(detections):
            self.spawn_new_series()

        if self.detection_series:
            self.detection_series.add_frame(frame)

        if detections:
            self.detection_series.inc_detections()

        if self.should_send_first_notification():
            self.send_first_notification()

        if self.detection_lapse_exceeded() or self.max_life_reached():
            self.terminate_detection_series()

    
    def can_send_notification(self):
        if not self.last_notification_sent_at:
            return True

        time_since_last_notification = time() - self.last_notification_sent_at
        can_send = time_since_last_notification > self.min_notification_interval

        return can_send

    def send_first_notification(self):
        self.last_notification_sent_at = time()
        self.detection_series.send_first_notification()


    def should_send_first_notification(self):
        not_in_series = not self.detection_series
        cannot_send = not self.can_send_notification()
        already_sent = self.detection_series and self.detection_series.first_notification_was_sent()

        if cannot_send and not already_sent:
            print('New person detected, but cannot send:\tToo soon!')

        if not_in_series or cannot_send or already_sent:
            return False

        duration_ok = self.detection_series.detection_duration_is_long_enough()
        ratio_ok = self.detection_series.detection_ratio_is_high_enough()

        should_send = duration_ok and ratio_ok

        return should_send


    def terminate_detection_series(self):
        if self.detection_series and self.detection_series.first_notification_was_sent():
            self.detection_series.process_series()
        
        self.detection_series = None

    def new_detection_series_needed(self, detections):
        return detections and not self.detection_series

    def max_life_reached(self):
        max_reached = self.detection_series and self.detection_series.max_life_reached()

        if max_reached:
            print('Max life reached!')

        return max_reached

    def detection_lapse_exceeded(self):
        lapse_exceeded = self.detection_series and self.detection_series.detection_lapse_interval_exceeded()

        if lapse_exceeded:
            print('Detection lapse exceeded!')

        return lapse_exceeded

    
