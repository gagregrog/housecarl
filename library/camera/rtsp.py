from library.camera.video import Video

class RTSP(Video):
    def __init__(self, config, frame_handler=None, on_exit=None):
        self.rtsp_url = None
        self.expected_types = {
            'rtsp_url': str
        }
        self.vs_args = (config.get('rtsp_url'),)
        super().__init__(config, frame_handler, on_exit)
