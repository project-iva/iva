from __future__ import annotations

from queue import Queue
from threading import Thread
from typing import Tuple, Optional, List

from backend_client.client import BackendClient
from events.events import UtteranceEvent, UtteranceIntentEvent
from intent_classifier.classifier import IntentClassifier
from interactions.output_provider import OutputProvider


class UtteranceEventHandler(Thread):
    """
    Obtains utterance intent classification and creates event for this intent
    Depending on the configuration we can ask user to confirm the intent classification to obtain more training data
    Furthermore, the utterance and intent classification are stored for later re-training
    """

    def __init__(self, event_queue: Queue, classifier: IntentClassifier, iva: Iva):
        super().__init__()
        self.event_queue = event_queue
        self.classifier = classifier
        self.iva = iva

    def run(self):
        while True:
            event: UtteranceEvent = self.event_queue.get()
            print(f'Handling {event}')
            # Classify utterance
            intent_prediction = self.classifier.request_classification(event.utterance).get()
            sorted_intent_prediction = sorted(intent_prediction.items(), key=lambda item: item[1], reverse=True)

            # TODO: handle case if there are on intents available
            intent, confidence = sorted_intent_prediction[0]

            if self.iva.config.ask_user_to_confirm_intent_prediction \
                    and confidence < self.iva.config.ask_user_to_confirm_intent_prediction_for_confidence_lower_than:
                confirmed_intent = self.__confirm_intent_prediction(event, sorted_intent_prediction)
                if confirmed_intent:
                    intent = confirmed_intent

            # Handle intent
            self.__handle_intent(intent, event.output_provider)

    def __confirm_intent_prediction(self, event: UtteranceEvent, sorted_intent_prediction: List) -> Optional[str]:
        if not (event.input_provider and event.output_provider):
            return None

        # Present the user with intent confirmation choices
        intent_choices, message = self.__construct_choices_and_message(sorted_intent_prediction)
        event.output_provider.output(message)
        choice = int(event.input_provider.get_input())

        # Check choice validity
        while choice not in range(0, len(intent_choices)):
            event.output_provider.output('Invalid choice, try again')
            choice = int(event.input_provider.get_input())

        #  Process user choice
        chosen_intent = intent_choices[choice]
        print(f'chosen intent: {chosen_intent}')
        intent = self.__process_and_store_intent(event, sorted_intent_prediction, chosen_intent)
        return intent

    def __construct_choices_and_message(self, intent_prediction: List) -> Tuple[list, str]:
        intent_choices = ['SKIP']
        message = '0 SKIP\n'
        for index, (intent, confidence) in enumerate(intent_prediction, 1):
            intent_choices.append(intent)
            message += f'{index} {intent} ({confidence})\n'
        intent_choices.append('ADD_A_NEW_INTENT')
        message += f'{len(intent_choices) - 1} {intent_choices[-1]}'
        return intent_choices, message

    def __process_and_store_intent(self, event: UtteranceEvent, sorted_intent_prediction: List,
                                   chosen_intent: str):
        if chosen_intent == 'ADD_A_NEW_INTENT':
            event.output_provider.output('What should be the new intent called?')
            new_intent = event.input_provider.get_input()
            BackendClient.post_training_instance_for_new_intent(event.utterance, new_intent)
            # Refresh template with new intent
            self.classifier.refresh_intent_classification_template()
            return new_intent

        user_intent = chosen_intent
        if chosen_intent == 'SKIP':
            # assume the classifier made a correct prediction and store the sample
            user_intent, _ = sorted_intent_prediction[0]
        BackendClient.post_training_instance_for_intent(event.utterance, user_intent)
        return user_intent

    def __handle_intent(self, intent: str, output_provider: Optional[OutputProvider]):
        try:
            # Try to convert to an utterance intent
            utterance_intent = UtteranceIntentEvent.Intent(intent.upper())
        except ValueError:
            print(f'Unknown intent {intent}')
            return
        else:
            utterance_intent_event = UtteranceIntentEvent(utterance_intent, output_provider)
            self.iva.event_scheduler.schedule_event(utterance_intent_event)
