from queue import Queue
from threading import Thread

from backend_client.client import BackendClient


class IntentClassifier(Thread):
    def __init__(self):
        super().__init__()
        self.intent_classification_template = {}
        self.refresh_intent_classification_template()
        self.classification_requests = Queue()

    def run(self):
        print(f'Intent classifier started!')
        while True:
            utterance, result_queue = self.classification_requests.get()
            classification_result = self.__classify(utterance)
            result_queue.put(classification_result)
            self.classification_requests.task_done()

    def request_classification(self, utterance: str):
        result_queue = Queue()
        self.classification_requests.put((utterance, result_queue))
        return result_queue

    def __classify(self, utterance: str) -> dict:
        template = self.intent_classification_template.copy()
        classification_result = {
            'INTRODUCTION': 0.7,
            'GET_TIME': 0.2,
            'SAY': 0.1
        }
        template.update(classification_result)
        return template

    def refresh_intent_classification_template(self):
        possible_intents = BackendClient.get_intents()
        self.intent_classification_template = {intent.intent: 0 for intent in possible_intents}
