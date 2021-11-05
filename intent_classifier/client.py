import os

import requests


class IntentClassifierClient:
    def __init__(self):
        self.url = os.environ.get('INTENT_CLASSIFIER_URL')
        self.jwt = os.environ.get('INTENT_CLASSIFIER_JWT')

    def make_classification_request(self, utterance: str) -> dict:
        headers = {
            'Authorization': f'Bearer {self.jwt}'
        }
        data = {
            'utterance': utterance
        }
        response = requests.post(self.url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
