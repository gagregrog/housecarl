from time import time

from library import utility
from library.detection_series import DetectionSeries
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
