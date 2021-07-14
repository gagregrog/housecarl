from time import time

from housecarl.library import utility
from housecarl.library.monitor.detection_series import DetectionSeries

class Monitor:
    def __init__(self, config, writer=None, pushover=None):
        self.config = config
        self.__writer = writer
        self.__pushover = pushover
        self.__last_detections = []
        self.__detection_series = None
        self.__last_series_ended_at = None

    def __spawn_new_series(self):
        utility.info('Person detected! Spawing new detection series.')
        self.__detection_series = DetectionSeries(self.config)

    def __in_timeout(self):
        if self.__detection_series:
            return False

        if not self.__last_series_ended_at:
            time_ok = True
        else:
            time_since_last_series = time() - self.__last_series_ended_at
            time_ok = time_since_last_series >= self.config.get('post_detection_debounce')

        return not time_ok

    def __send_first_notification(self):
        utility.info('Sending push notification!')
        (frame, label, confidence) = self.__detection_series.get_best_frame_tuple()
        capital_label = utility.capitalize(label)
        round_conf = utility.get_precision(confidence, 3)

        message = '{} detected with confidence {}'.format(capital_label, round_conf)
        self.__pushover.send_push_notification(message, frame)

    def __handle_series_activation(self):
        utility.info('Detection verified.')

        # if we have push notifications, send the alert
        if self.__pushover is not None:
            self.__send_first_notification()
        
        # if we are recording, start a recording
        if self.__writer is not None:
            self.__writer.start()


    def __terminate_detection_series(self):
        # we can assume the detection threshold was met,
        # otherwise we wouldn't have sent a notification
        if self.__detection_series.series_is_active():
            self.__last_series_ended_at = time()
            utility.info('Waiting {} seconds before starting new detection series.\n'.format(self.config.get('post_detection_debounce')))
            
            # If we've been recording, finish the recording
            self.finish_recording()
        
        self.__last_detections = []
        self.__detection_series = None

    def __new_detection_series_needed(self, detections):
        return detections and not self.__detection_series

    def handle_detections(self, detections, frame):
        # always add the frame
        if self.__writer is not None:
            self.__writer.update(frame)
            
        # stale detections only occur when threaded
        stale_detections = self.__last_detections is detections

        # update the cached detections so we can check again next loop
        if not stale_detections:
            self.__last_detections = detections

        # If we've recently ended a series, pause for a beat
        if self.__in_timeout():
            return
            
        # there are detections and there is not currently a series
        if self.__new_detection_series_needed(detections):
            self.__spawn_new_series()

        elif not self.__detection_series:
            # Nothing below applies if we're not in a series
            return

        # frames come through unprocessed when threaded, 
        # but we only want to count against frames that were
        # processed for detections
        if not stale_detections:
            self.__detection_series.inc_frames_processed()

            if detections:
                self.__detection_series.process_frame(frame, detections)

        # if the detection minimums are met, the series will activate
        if self.__detection_series.series_is_activating():
            return self.__handle_series_activation()

        max_life_reached = self.__detection_series.max_life_reached()
        detection_lapse_exceeded = self.__detection_series.detection_lapse_interval_exceeded()

        if max_life_reached or detection_lapse_exceeded:
            if detection_lapse_exceeded:
                utility.info('No detections for {} seconds'.format(self.config.get('detection_lapse_timeout')))
            else:
                utility.info('Max life of {} seconds reached'.format(self.config.get('max_detection_duration')))

            self.__terminate_detection_series()

    def finish_recording(self):
        if self.__writer and self.__writer.is_recording():
            self.__writer.finish()
