import requests
import numpy as np
from threading import Thread

from library import utility
from library.camera.image import mat_to_bytes

PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"

class Pushover:
    def __init__(self, config):
        utility.set_properties(config, self)
        self.__verify_tokens(config)

    def __verify_tokens(self, config):
        if self.mock:
            return
        elif not self.user_key:
            raise Exception("config.pushover_user_key is required")
        elif not self.api_token:
            raise Exception("config.pushover_api_token is required")

    def __send_push_notification(self, message: str, image: np.ndarray = None):
        kwargs = {
            "data": {
                "token": self.api_token,
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
            utility.error('Pushover error!\n')
            print(json_response)

    def send_push_notification(self, message: str, image: np.ndarray = None):
        if self.mock:
            return utility.info('PUSHOVER_MOCK: {}'.format(message))

        thread = Thread(target=self.__send_push_notification, args=(message, image))
        thread.start()
        