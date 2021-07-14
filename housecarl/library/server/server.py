import os
from waitress import serve
from threading import Thread
from flask import jsonify, request
from werkzeug.utils import secure_filename
from flask import Flask, send_file, make_response, send_from_directory

from housecarl.library.common import utility, constants

def is_video_file(video_name):
    file_ending = video_name[-4:].lower()

    return file_ending in ['.ogv', '.ogg']

def should_serve_index(path):
    return '.' not in path or is_video_file(path)

class Server:
    def __init__(self, cli, config):
        self.cli = cli
        self.config = config
        self.__thread = None
        self.__server_started = False

        # resolve the video directory
        config.set('video_dir', utility.get_video_dir(config.get('video_dir')))

        flask_app = Flask(__name__, static_url_path='/build/static')
        self.__flask_app = flask_app

        # Serve React App
        @flask_app.route('/', defaults={'path': ''})
        @flask_app.route('/<path:path>')
        def serve(path):
            if path != "" and os.path.exists(os.path.join(constants.build_path, path)):
                resp = make_response(send_from_directory(constants.build_path, path), 200)

                return resp
            elif should_serve_index(path):
                resp = make_response(send_from_directory(constants.build_path, 'index.html'), 200)

                return resp
            else:
                return jsonify('Not Found'), 404


        # a health check endpoint
        @flask_app.route('/health', methods=['GET'])
        def health():
            return jsonify('OK'), 200

        # a route at /api/config that returns the full cli config
        @flask_app.route('/api/config', methods=['GET'])
        def get_config():
            return jsonify(self.cli.dict())

        # a route at /api/confif/<group> that returns the config for the given group
        @flask_app.route('/api/config/<group>', methods=['GET'])
        def get_config_group(group):
            # if the group is not valid, return a 404
            if not self.cli.is_valid_group_name(group):
                return jsonify('Not Found'), 404

            return jsonify(self.cli.get_group_dict(group))

        # add a /api/config route that sets config values
        @flask_app.route('/api/config', methods=['POST'])
        def set_config():
            data = request.get_json()

            # return a 400 error if the request is not valid
            # the request must include a key, value, and group
            if not data or not data.get('key') or not data.get('value') or not data.get('group'):
                return jsonify({
                    'error': 'Invalid request',
                    'message': 'The request must include a key, value, and group.'
                }), 400

            # try to set the value of the config key and return an error if it fails
            try:
                cli.set(data.get('group'), data.get('key'), data.get('value'))
            except Exception as e:
                return jsonify({
                    'error': 'Unable to set config',
                    'message': str(e)
                }), 400

            # return a success message and the updated config group
            return jsonify({
                'success': 'Config updated',
                'config': cli.get_group_dict(data.get('group'))
            })

            
        @flask_app.route("/api/videos")
        def get_videos():
            if not os.path.isdir(self.config.get('video_dir')):
                return jsonify({'message': 'Video directory does not exists'}), 404

            video_array = []
            dates = os.listdir(self.config.get('video_dir'))
            dates.sort()

            for date in dates:
                date_path = os.path.join(self.config.get('video_dir'), date)
                
                if os.path.isdir(date_path):
                    video_names = os.listdir(date_path)
                    video_names.sort()
                    filtered_video_names = [video_name for video_name in video_names if is_video_file(video_name)]
                    video_array.append({
                        "date": date,
                        "videos": filtered_video_names
                    })

            return jsonify(video_array)

        @flask_app.route('/api/videos/<video_date>/<video_name>')
        def serve_video(video_date, video_name):
            safe_video_date = secure_filename(video_date)
            safe_video_name = secure_filename(video_name)
            video_path = os.path.join(self.config.get('video_dir'), safe_video_date, safe_video_name)
            resp = make_response(send_file(video_path, 'video/ogg'))
            resp.headers['Content-Disposition'] = 'inline'
            return resp

    def __run(self):
        utility.info('Starting housecarl server on port {}.'.format(self.config.get('port')))
        utility.info('Serving videos from {}'.format(self.config.get('video_dir')))
        self.__server_started = True

        if self.config.get('server_debug'):
            self.__flask_app.run(
                debug=True,
                port=self.config.get('port')
            )
        else:
            serve(self.__flask_app, listen='*:{}'.format(self.config.get('port')))

    def start(self):
        if not self.__server_started:
            if not self.config.get('server_only'):
                self.__thread = Thread(target=self.__run, args=())
                self.__thread.daemon = True
                self.__thread.start()
            else:
                self.__run()
