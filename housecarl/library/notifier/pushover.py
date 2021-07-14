import requests
import numpy as np
from threading import Thread

from housecarl.library import utility
from housecarl.library.camera.image import mat_to_bytes

PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"

class Pushover:
    def __init__(self, config):
        self.config = config
        self.__verify_tokens()

    def __verify_tokens(self):
        if self.config.get('mock'):
            return
        elif not self.config.get('user_key'):
            raise Exception("config.pushover.user_key is required")
        elif not self.config.get('api_token'):
            raise Exception("config.pushover.api_token is required")

    def __send_push_notification(self, message: str, image: np.ndarray = None):
        kwargs = {
            "data": {
                "token": self.config.get('api_token'),
                "user": self.config.get('user_key'),
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
            utility.error('Pushover error!\n')
            print(json_response)

    def send_push_notification(self, message: str, image: np.ndarray = None):
        if self.config.get('mock'):
            return utility.info('PUSHOVER_MOCK: {}'.format(message))

        thread = Thread(target=self.__send_push_notification, args=(message, image))
        thread.start()
        