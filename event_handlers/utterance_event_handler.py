from threading import Thread
from events.events import UtteranceEvent
from slack_client.handler import SlackClientHandler
from slack_client.session import SlackSession


class UtteranceEventHandler(Thread):
    def __init__(self, event: UtteranceEvent, slack_client: SlackClientHandler):
        super().__init__()
        self.event = event
        self.slack_client = slack_client

    def run(self):
        print(f'Handling {self.event}')
        session = SlackSession()
        self.slack_client.set_active_session(session)
        while True:
            utterance = session.wait_for_an_utterance()
            print(f'awaited utterance: {utterance}')
            if utterance == 'exit':
                break

        self.slack_client.close_active_session()
