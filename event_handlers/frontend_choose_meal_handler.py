from __future__ import annotations

from queue import Queue
from threading import Thread
from typing import List

from backend_client.models import Meal
from control_session.session import PresenterControlSession, PresenterItem, ControllerAction, PresenterSession, \
    PresenterSessionType
from events.events import ChooseMealEvent


class FrontEndChooseMealHandler(Thread):
    def __init__(self, choose_meal_event: ChooseMealEvent, iva: Iva):
        super().__init__()
        self.choose_meal_event = choose_meal_event
        self.iva = iva
        self.event_queue = Queue(1)

    def run(self):
        print(f'Handling {self.choose_meal_event}')

        presenter_session = self.get_presenter_session()
        control_session = PresenterControlSession(presenter_session, self.event_queue, self.iva.socket_server)
        self.iva.register_control_session(control_session)
        control_session.handle_action(ControllerAction.START_PRESENTING)

        choice = self.event_queue.get()
        self.event_queue.task_done()
        print(choice)
        # BackendClient.post_chosen_meal(chosen_meal_id)

    def get_presenter_session(self) -> PresenterSession:
        items = self.get_meal_items()
        return PresenterSession(PresenterSessionType.MEAL_CHOICES, items)

    def get_meal_items(self) -> List[PresenterItem]:
        # possible_meals = BackendClient.get_possible_meals()
        possible_meals = [Meal(1, 'meal 1', 'b', 1, []), Meal(2, 'meal 2', 'b', 1, [])]
        presenter_items = []
        last_meal_index = len(possible_meals) - 1
        for index, meal in enumerate(possible_meals):
            valid_actions = [ControllerAction.CONFIRM]
            if index == 0:
                item = PresenterItem(meal.dict, valid_actions + [ControllerAction.NEXT])
            elif index == last_meal_index:
                item = PresenterItem(meal.dict, valid_actions + [ControllerAction.PREV])
            else:
                item = PresenterItem(meal.dict, valid_actions + [ControllerAction.NEXT, ControllerAction.PREV])
            presenter_items.append(item)

        return presenter_items
