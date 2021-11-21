from __future__ import annotations

from queue import Queue
from threading import Thread
from typing import List

from backend_client.client import BackendClient
from models.meal import Meal
from control_session.session import PresenterControlSession, PresenterItem, ControlSessionAction, PresenterSession, \
    PresenterSessionType
from events.events import ChooseMealEvent


class ChooseMealEventHandler(Thread):
    """
    Handles choose meal event by showing menu in the frontend and creating a control session to handle user input
    """

    def __init__(self, event_queue: Queue, iva: Iva):
        super().__init__()
        self.event_queue = event_queue
        self.iva = iva

    def run(self):
        while True:
            event: ChooseMealEvent = self.event_queue.get()
            print(f'Handling {event}')

            control_session_event_queue = Queue(1)
            possible_meals = BackendClient.get_possible_meals()
            presenter_session = self.__get_presenter_session(possible_meals)
            control_session = PresenterControlSession(presenter_session, control_session_event_queue,
                                                      self.iva.socket_server)
            session_uuid = self.iva.register_control_session(control_session)
            control_session.handle_action(ControlSessionAction.START_PRESENTING)

            choice = control_session_event_queue.get()
            control_session_event_queue.task_done()
            self.iva.unregister_control_session(session_uuid)

            # store the choice in the backend
            chosen_meal_id = possible_meals[choice].id
            BackendClient.post_chosen_meal(chosen_meal_id)

    def __get_presenter_session(self, possible_meals: List[Meal]) -> PresenterSession:
        items = self.__get_meal_items(possible_meals)
        return PresenterSession(PresenterSessionType.MEAL_CHOICES, items)

    def __get_meal_items(self, possible_meals: List[Meal]) -> List[PresenterItem]:
        presenter_items = []
        last_meal_index = len(possible_meals) - 1
        for index, meal in enumerate(possible_meals):
            valid_actions = [ControlSessionAction.CONFIRM]
            if index == 0 and index == last_meal_index:
                item = PresenterItem(meal.dict, valid_actions)
            elif index == 0:
                item = PresenterItem(meal.dict, valid_actions + [ControlSessionAction.NEXT])
            elif index == last_meal_index:
                item = PresenterItem(meal.dict, valid_actions + [ControlSessionAction.PREV])
            else:
                item = PresenterItem(meal.dict, valid_actions + [ControlSessionAction.NEXT, ControlSessionAction.PREV])
            presenter_items.append(item)

        return presenter_items
