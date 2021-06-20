import os
from flask import jsonify
from threading import Thread
from werkzeug.utils import secure_filename
from flask import Flask, send_file, make_response, send_from_directory

from housecarl.library import utility, constants

def is_video_file(video_name):
    file_ending = video_name[-4:].lower()

    return file_ending in ['.ogv', '.ogg']

def should_serve_index(path):
    return '.' not in path or is_video_file(path)

class Server:
    def __init__(self, config):
        utility.set_properties(config, self)
        self.__thread = None
        self.__server_started = False
        self.video_dir = utility.get_video_dir(self.video_dir)

        app = Flask(__name__, static_url_path='/build/static')
        self.__app = app

        # Serve React App
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve(path):
            if path != "" and os.path.exists(os.path.join(constants.build_path, path)):
                resp = make_response(send_from_directory(constants.build_path, path), 200)

                return resp
            elif should_serve_index(path):
                resp = make_response(send_from_directory(constants.build_path, 'index.html'), 200)

                return resp
            else:
                return jsonify('Not Found'), 404


        @app.route("/api/videos")
        def get_videos():
            if not os.path.isdir(self.video_dir):
                return jsonify('Video directory does not exists'), 404

            video_array = []
            dates = os.listdir(self.video_dir)
            dates.sort()

            for date in dates:
                date_path = os.path.join(self.video_dir, date)
                
                if os.path.isdir(date_path):
                    video_names = os.listdir(date_path)
                    video_names.sort()
                    filtered_video_names = [video_name for video_name in video_names if is_video_file(video_name)]
                    video_array.append({
                        "date": date,
                        "videos": filtered_video_names
                    })

            return jsonify(video_array)

        @app.route('/api/videos/<video_date>/<video_name>')
        def serve_video(video_date, video_name):
            safe_video_date = secure_filename(video_date)
            safe_video_name = secure_filename(video_name)
            video_path = os.path.join(self.video_dir, safe_video_date, safe_video_name)
            resp = make_response(send_file(video_path, 'video/ogg'))
            resp.headers['Content-Disposition'] = 'inline'
            return resp

    def __run(self):
        utility.info('Starting housecarl server on port {}.'.format(self.port))
        utility.info('Serving videos from {}'.format(self.port, self.video_dir))
        self.__server_started = True
        self.__app.run(
            debug=self.server_only,
            port=self.port
        )

    def start(self):
        if not self.__server_started:
            if not self.server_only:
                self.__thread = Thread(target=self.__run, args=())
                self.__thread.daemon = True
                self.__thread.start()
            else:
                self.__run()
