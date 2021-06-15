import os
from threading import Thread
from werkzeug.utils import secure_filename
from flask import Flask, send_file, make_response, render_template

from housecarl.library import utility

class Server:
    def __init__(self, config):
        utility.set_properties(config, self)
        self.__thread = None
        self.video_dir = utility.get_video_dir(self.video_dir)

        app = Flask(__name__)
        self.__app = app
        
        @app.route("/")
        def index():
            return render_template("index.html")

        @app.route("/videos")
        def get_videos():
            days = os.listdir(self.video_dir)
            data = {}

            for day in days:
                folder = os.path.join(self.video_dir, day)
                
                if os.path.isdir(folder):
                    videos = os.listdir(folder)
                    data[day] = videos

            return data

        @app.route('/videos/<vid_name>')
        def serve_video(vid_name):
            safe_video_name = secure_filename(vid_name)
            vid_path = os.path.join(self.video_dir, safe_video_name)
            resp = make_response(send_file(vid_path, 'video/ogg'))
            resp.headers['Content-Disposition'] = 'inline'
            return resp

    def __run(self):
        self.__app.run(
            debug=False,
            port=self.port
        )

    def start(self):
        if self.__thread is None:
            utility.info('Starting video server on port {}, serving videos from {}'.format(self.port, self.video_dir))

            self.__thread = Thread(target=self.__run, args=())
            self.__thread.daemon = True
            self.__thread.start()
