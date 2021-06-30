from __future__ import annotations
from queue import Queue
from threading import Thread

from backend_client.client import BackendClient
from events.events import ChooseMealEvent, ChoiceEvent


class ChooseMealHandler(Thread):
    def __init__(self, choose_meal_event: ChooseMealEvent, iva: Iva):
        super().__init__()
        self.choose_meal_event = choose_meal_event
        self.iva = iva
        self.event_queue = Queue(1)

    def run(self):
        print(f'Handling {self.choose_meal_event}')
        possible_meals = BackendClient.get_possible_meals()
        choice_to_meal_map = {
            choice: meal for choice, meal in enumerate(possible_meals, start=1)
        }

        self.iva.register_event_type_listener(ChoiceEvent, self.event_queue)

        cancel_choice = len(possible_meals) + 1
        slack_message = 'Choose meal:\n'
        for choice in choice_to_meal_map:
            meal = choice_to_meal_map[choice]
            slack_message += f'\t{choice}) {meal.name} - {meal.kcal} kcal\n'
        slack_message += f'\t{cancel_choice}) Cancel'
        self.iva.slack_client.send_message(slack_message)

        choice_event = self.event_queue.get()
        self.event_queue.task_done()
        choice = choice_event.choice

        if choice == cancel_choice:
            return

        if choice not in choice_to_meal_map:
            raise Exception('Invalid choice')

        chosen_meal_id = choice_to_meal_map[choice].id
        BackendClient.post_chosen_meal(chosen_meal_id)
