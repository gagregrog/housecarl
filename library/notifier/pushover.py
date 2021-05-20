import requests
import numpy as np
from threading import Thread

from library import utility
from library.camera.image import mat_to_bytes

PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"

class Pushover:
    def __init__(self, config):
        self.verify_tokens(config)

    def verify_tokens(self, config):
        self.mock = False
        self.user_key = config["pushover_user_key"]
        self.app_token = config["pushover_app_token"]

        if config.get("mock_pushover"):
            self.mock = True
        elif not self.user_key:
            raise Exception("config.pushover_user_key is required")
        elif not self.app_token:
            raise Exception("config.pushover_app_token is required")

    def send_push_notification(self, message: str, image: np.ndarray = None):
        if self.mock:
            return utility.info('PUSHOVER_MOCK: {}'.format(message))

        thread = Thread(target=self.__send_push_notification, args=(message, image))
        thread.start()

    def __send_push_notification(self, message: str, image: np.ndarray = None):
        kwargs = {
            "data": {
                "token": self.app_token,
                "user": self.user_key,
                "message": message
            }
        }

        if image is not None:
            im_bytes = mat_to_bytes(image)
            if im_bytes:
                kwargs["files"] = {
                    "attachment": ("image.jpg", im_bytes, "image/jpeg")
                }
            else:
                utility.warn('Could not convert image to byes.')

        r = requests.post(PUSHOVER_API_URL, **kwargs)

        json_response = r.json()

        if json_response.get('status') != 1:
            utility.error('Pushover error!')
            print(json_response)
        