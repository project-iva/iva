import os
from enum import Enum
import requests


class RaspberryClient:
    class Action(str, Enum):
        SCREEN_ON = 'SCREEN_ON'
        SCREEN_OFF = 'SCREEN_OFF'
        SAY = 'SAY'

    @staticmethod
    def send_action_request(action: Action, extra_data: dict = None):
        endpoint = os.environ.get('RASPBERRY_CLIENT_URL')
        data = {
            'action': action.value
        }

        if extra_data:
            data.update(extra_data)

        requests.post(endpoint, data=data)
