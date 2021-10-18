from queue import Queue


class SlackSession:
    def __init__(self):
        self.utterances = []
        self.queue = Queue()
        self.waiting_for_an_utterance = False

    def add_new_utterance(self, utterance: str):
        self.utterances.append(utterance)
        if self.waiting_for_an_utterance:
            self.waiting_for_an_utterance = False
            self.queue.put(utterance)

    def wait_for_an_utterance(self) -> str:
        self.waiting_for_an_utterance = True
        return self.queue.get()
