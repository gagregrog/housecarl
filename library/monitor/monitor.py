from time import time

from library import utility
from library.camera.writer import Writer
from library.notifier.pushover import Pushover
from library.monitor.detection_series import DetectionSeries

class Monitor:
    def __init__(self, config):
        self.debug = config['debug']
        self.config = config
        self.last_detections = []
        self.writer = None
        self.detection_series = None
        self.last_series_ended_at = None

        # number of seconds to rest after a detection series
        self.post_detection_debounce = config['post_detection_debounce']

        self.initialize_writer()
        self.initialize_pushover()

    def initialize_writer(self):
        if self.config['out_dir']:
            self.writer = Writer(self.config)

    def initialize_pushover(self):
        if self.config.get('mock_pushover') or self.config['pushover_user_key'] and self.config['pushover_app_token']:
            self.pushover = Pushover(self.config)
        else:
            self.pushover = None
            utility.info('Pushover keys not found. Notifications disabled.')

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
        # always add the frame
        if self.writer:
            self.writer.update(frame)
            
        # stale detections only occur when threaded
        stale_detections = self.last_detections is detections

        # update the cached detections so we can check again next loop
        if not stale_detections:
            self.last_detections = detections

        # If we've recently ended a series, pause for a beat
        if self.in_timeout():
            return
            
        # there are detections and there is not currently a series
        if self.new_detection_series_needed(detections):
            self.spawn_new_series()

        elif not self.detection_series:
            # Nothing below applies if we're not in a series
            return

        # frames come through unprocessed when threaded, 
        # but we only want to count against frames that were
        # processed for detections
        if not stale_detections:
            self.detection_series.inc_frames_processed()

            if detections:
                self.detection_series.process_frame(frame, detections)

        # if the detection minimums are met, the series will activate
        if self.detection_series.series_is_activating():
            return self.handle_series_activation()

        max_life_reached = self.detection_series.max_life_reached()
        detection_lapse_exceeded = self.detection_series.detection_lapse_interval_exceeded()

        if max_life_reached or detection_lapse_exceeded:
            if detection_lapse_exceeded:
                utility.info('No detections for {} seconds'.format(self.config['detection_lapse_timeout']))
            else:
                utility.info('Max life of {} seconds reached'.format(self.config['max_detection_duration']))

            self.terminate_detection_series()

    def send_first_notification(self):
        utility.info('Sending push notification!')
        (frame, label, confidence) = self.detection_series.get_best_frame()
        capital_label = utility.capitalize(label)
        round_conf = utility.get_precision(confidence, 3)

        message = '{} detected with confidence {}'.format(capital_label, round_conf)
        self.pushover.send_push_notification(message, frame)

    def handle_series_activation(self):
        utility.info('Person verified.')

        # if we have push notifications, send the alert
        if self.pushover:
            self.send_first_notification()
        
        # if we are recording, start a recording
        if self.writer:
            self.writer.start_recording()


    def terminate_detection_series(self):
        # we can assume the detection threshold was met,
        # otherwise we wouldn't have sent a notification
        if self.detection_series.series_is_active():
            self.last_series_ended_at = time()
            utility.info('Waiting {} seconds before starting new detection series.\n'.format(self.config['post_detection_debounce']))
            
            # If we've been recording, finish the recording
            self.finish_recording()
        
        self.last_detections = []
        self.detection_series = None

    def new_detection_series_needed(self, detections):
        return detections and not self.detection_series

    def finish_recording(self):
        if self.writer and self.writer.is_recording():
            self.writer.finish()
