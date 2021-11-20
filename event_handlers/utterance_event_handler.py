from __future__ import annotations
from threading import Thread
from typing import Tuple, Optional

from backend_client.client import BackendClient
from events.events import UtteranceEvent, UtteranceIntentEvent
from intent_classifier.classifier import IntentClassifier


class UtteranceEventHandler(Thread):
    def __init__(self, event: UtteranceEvent, classifier: IntentClassifier, iva: Iva):
        super().__init__()
        self.event = event
        self.classifier = classifier
        self.iva = iva

    def run(self):
        print(f'Handling {self.event}')
        # Classify utterance
        intent_prediction = self.classifier.request_classification(self.event.utterance).get()
        sorted_intent_prediction = sorted(intent_prediction.items(), key=lambda item: item[1], reverse=True)

        # TODO: handle case if there are on intents available
        intent, _ = sorted_intent_prediction[0]

        # TODO: should confirm? check config
        if self.iva.config.ask_user_to_confirm_intent_prediction:
            confirmed_intent = self.confirm_intent_prediction(sorted_intent_prediction)
            if confirmed_intent:
                intent = confirmed_intent

        # Handle intent
        self.handle_intent(intent)

    def confirm_intent_prediction(self, sorted_intent_prediction) -> Optional[str]:
        if not (self.event.input_provider and self.event.output_provider):
            return None

        # Present the user with intent confirmation choices
        intent_choices, message = self.construct_choices_and_message(sorted_intent_prediction)
        self.event.output_provider.output(message)
        choice = int(self.event.input_provider.get_input())

        # Check choice validity
        while choice not in range(0, len(intent_choices)):
            self.event.output_provider.output('Invalid choice, try again')
            choice = int(self.event.input_provider.get_input())

        #  Process user choice
        chosen_intent = intent_choices[choice]
        print(f'chosen intent: {chosen_intent}')
        intent = self.process_and_store_intent(self.event.utterance, sorted_intent_prediction, chosen_intent)
        return intent

    def construct_choices_and_message(self, intent_prediction) -> Tuple[list, str]:
        intent_choices = ['SKIP']
        message = '0 SKIP\n'
        for index, (intent, confidence) in enumerate(intent_prediction, 1):
            intent_choices.append(intent)
            message += f'{index} {intent} ({confidence})\n'
        intent_choices.append('ADD_A_NEW_INTENT')
        message += f'{len(intent_choices) - 1} {intent_choices[-1]}'
        return intent_choices, message

    def process_and_store_intent(self, message, sorted_intent_prediction, chosen_intent):
        if chosen_intent == 'ADD_A_NEW_INTENT':
            self.event.output_provider.output('What should be the new intent called?')
            new_intent = self.event.input_provider.get_input()
            BackendClient.post_training_instance_for_new_intent(message, new_intent)
            # Refresh template with new intent
            self.classifier.refresh_intent_classification_template()
            return new_intent

        user_intent = chosen_intent
        if chosen_intent == 'SKIP':
            # assume the classifier made a correct prediction and store the sample
            user_intent, _ = sorted_intent_prediction[0]
        BackendClient.post_training_instance_for_intent(message, user_intent)
        return user_intent

    def handle_intent(self, intent: str):
        try:
            # Try to convert to an utterance intent
            utterance_intent = UtteranceIntentEvent.Intent(intent.upper())
        except ValueError:
            print(f'Unknown intent {intent}')
            return
        else:
            utterance_intent_event = UtteranceIntentEvent(utterance_intent, self.event.output_provider)
            self.iva.event_scheduler.schedule_event(utterance_intent_event)
