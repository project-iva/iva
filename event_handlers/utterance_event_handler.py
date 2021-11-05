from threading import Thread
from typing import Tuple

from backend_client.client import BackendClient
from events.events import UtteranceEvent
from intent_classifier.classifier import IntentClassifier
from slack_client.handler import SlackClientHandler
from slack_client.session import SlackSession


class UtteranceEventHandler(Thread):
    def __init__(self, event: UtteranceEvent, slack_client: SlackClientHandler, classifier: IntentClassifier):
        super().__init__()
        self.event = event
        self.slack_client = slack_client
        self.classifier = classifier

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
        self.handle_chosen_intent(self.event.utterance, sorted_intent_prediction, chosen_intent, session)
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

    def handle_chosen_intent(self, message, sorted_intent_prediction, chosen_intent, session):
        if chosen_intent == 'ADD_A_NEW_INTENT':
            self.slack_client.send_message('What should be the new intent called?')
            new_intent = session.wait_for_an_utterance()
            BackendClient.post_training_instance_for_new_intent(message, new_intent)
            # Refresh template with new intent
            self.classifier.refresh_intent_classification_template()
        elif chosen_intent == 'SKIP':
            # assume the classifier made a correct prediction and store the sample
            highest_confidence_intent, _ = sorted_intent_prediction[0]
            BackendClient.post_training_instance_for_intent(message, highest_confidence_intent)
        else:
            BackendClient.post_training_instance_for_intent(message, chosen_intent)
