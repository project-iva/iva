import os
from enum import Enum
import requests


class RaspberryClient:
    class Action(str, Enum):
        SCREEN_ON = 'screen_on'
        SCREEN_OFF = 'screen_off'

    @staticmethod
    def send_action_request(action: Action):
        endpoint = os.environ.get('RASPBERRY_CLIENT_URL')
        data = {
            'action': action.value
        }
        requests.post(endpoint, data=data)
