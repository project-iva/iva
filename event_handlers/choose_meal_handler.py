from threading import Thread

from backend_client.client import BackendClient
from events.events import ChooseMealEvent


class ChooseMealHandler(Thread):
    def __init__(self, choose_meal_event: ChooseMealEvent):
        super().__init__()
        self.choose_meal_event = choose_meal_event

    def run(self):
        print(f'Handling {self.choose_meal_event}')
        possible_meals = BackendClient.get_possible_meals()
        choice_to_id_map = {
            choice: meal.id for choice, meal in enumerate(possible_meals, start=1)
        }
        print(choice_to_id_map)
        choice = 1
        chosen_meal_id = choice_to_id_map[choice]
        BackendClient.post_chosen_meal(chosen_meal_id)
