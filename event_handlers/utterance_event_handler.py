from datetime import datetime
from threading import Thread
from typing import Tuple

from backend_client.client import BackendClient
from event_scheduler import EventScheduler
from events.events import UtteranceEvent, RaspberryEvent
from intent_classifier.classifier import IntentClassifier
from raspberry_client.client import RaspberryClient
from slack_client.handler import SlackClientHandler
from slack_client.session import SlackSession


class UtteranceEventHandler(Thread):
    def __init__(self, event: UtteranceEvent, slack_client: SlackClientHandler, classifier: IntentClassifier,
                 event_scheduler: EventScheduler):
        super().__init__()
        self.event = event
        self.slack_client = slack_client
        self.classifier = classifier
        self.event_scheduler = event_scheduler

    def run(self):
        print(f'Handling {self.event}')

        intent_prediction = self.classifier.request_classification(self.event.utterance).get()
        sorted_intent_prediction = sorted(intent_prediction.items(), key=lambda item: item[1], reverse=True)
        intent_choices, message = self.construct_choices_and_message(sorted_intent_prediction)
        self.slack_client.send_message(message)

        session = SlackSession()
        self.slack_client.set_active_session(session)
        choice = int(session.wait_for_an_utterance())

        while choice < 0 or choice >= len(intent_choices):
            self.slack_client.send_message('Invalid choice, try again')
            choice = int(session.wait_for_an_utterance())

        chosen_intent = intent_choices[choice]
        print(f'chosen intent: {chosen_intent}')
        intent = self.process_and_store_intent(self.event.utterance, sorted_intent_prediction, chosen_intent, session)
        if intent:
            self.handle_intent(intent)
        self.slack_client.close_active_session()

    def construct_choices_and_message(self, intent_prediction) -> Tuple[list, str]:
        intent_choices = ['SKIP']
        message = '0 SKIP\n'
        for index, (intent, confidence) in enumerate(intent_prediction, 1):
            intent_choices.append(intent)
            message += f'{index} {intent} ({confidence})\n'
        intent_choices.append('ADD_A_NEW_INTENT')
        message += f'{len(intent_choices) - 1} {intent_choices[-1]}'
        return intent_choices, message

    def process_and_store_intent(self, message, sorted_intent_prediction, chosen_intent, session):
        if chosen_intent == 'ADD_A_NEW_INTENT':
            self.slack_client.send_message('What should be the new intent called?')
            new_intent = session.wait_for_an_utterance()
            BackendClient.post_training_instance_for_new_intent(message, new_intent)
            # Refresh template with new intent
            self.classifier.refresh_intent_classification_template()
            return

        user_intent = chosen_intent
        if chosen_intent == 'SKIP':
            # assume the classifier made a correct prediction and store the sample
            user_intent, _ = sorted_intent_prediction[0]
        BackendClient.post_training_instance_for_intent(message, user_intent)
        return user_intent

    def handle_intent(self, intent: str):
        print(f'Handling {intent} intent')
        dispatcher = {
            'introduce_yourself': self.handle_introduce_yourself_intent,
            'tell_time': self.handle_tell_time_intent,
            'turn_screen_on': self.handle_turn_screen_on_intent,
            'turn_screen_off': self.handle_turn_screen_off_intent
        }
        dispatcher[intent]()

    def handle_introduce_yourself_intent(self):
        self.slack_client.send_message('I am IVA.')

    def handle_tell_time_intent(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.slack_client.send_message(f'The time is {current_time}')

    def handle_turn_screen_on_intent(self):
        self.event_scheduler.schedule_event(RaspberryEvent(RaspberryClient.Action.SCREEN_ON))

    def handle_turn_screen_off_intent(self):
        self.event_scheduler.schedule_event(RaspberryEvent(RaspberryClient.Action.SCREEN_OFF))
