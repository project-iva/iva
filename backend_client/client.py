import os
from typing import List, Optional

import requests as requests
from uuid import UUID

from models.day_plan import DayPlan
from models.intent import Intent
from models.meal import Meal, ChosenMeal
from models.training_instance import TrainingInstance


class BackendClient:
    @staticmethod
    def get_backend_api_url() -> str:
        return os.environ.get('BACKEND_API_URL')

    @staticmethod
    def get_possible_meals() -> List[Meal]:
        base_api_url = BackendClient.get_backend_api_url()
        response = requests.get(f'{base_api_url}/possible-meals/')
        possible_meals = []
        for meal_dict in response.json():
            possible_meals.append(Meal.from_dict(meal_dict))
        return possible_meals

    @staticmethod
    def post_chosen_meal(meal_id: int):
        chosen_meal = ChosenMeal(meal_id)
        base_api_url = BackendClient.get_backend_api_url()
        headers = {'Content-type': 'application/json'}
        response = requests.post(f'{base_api_url}/meal-tracking-entries/', headers=headers, data=chosen_meal.json)
        response.raise_for_status()

    @staticmethod
    def get_current_day_plan() -> DayPlan:
        base_api_url = BackendClient.get_backend_api_url()
        response = requests.get(f'{base_api_url}/current-day-plan/')
        day_plan = DayPlan.from_dict(response.json())
        return day_plan

    @staticmethod
    def get_intents() -> List[Intent]:
        base_api_url = BackendClient.get_backend_api_url()
        response = requests.get(f'{base_api_url}/intents/')
        return [Intent.from_dict(json_intent) for json_intent in response.json()]

    @staticmethod
    def post_intent(intent: str) -> Intent:
        base_api_url = BackendClient.get_backend_api_url()
        data = {
            'intent': intent
        }
        response = requests.post(f'{base_api_url}/intents/', data=data)
        response.raise_for_status()
        return Intent.from_dict(response.json())

    @staticmethod
    def post_training_instance(message: str, intent_uuid: UUID):
        training_instance = TrainingInstance(message, str(intent_uuid))
        base_api_url = BackendClient.get_backend_api_url()
        headers = {'Content-type': 'application/json'}
        response = requests.post(f'{base_api_url}/training-instances/', data=training_instance.json, headers=headers)
        response.raise_for_status()

    @staticmethod
    def post_training_instance_for_intent(message: str, intent: str):
        def get_matching_intent(intent_name: str, intents: List[Intent]) -> Optional[Intent]:
            for intent in intents:
                if intent_name == intent.intent:
                    return intent
            return None

        intents = BackendClient.get_intents()
        matching_intent = get_matching_intent(intent, intents)
        if matching_intent:
            BackendClient.post_training_instance(message, matching_intent.uuid)

    @staticmethod
    def post_training_instance_for_new_intent(message: str, new_intent: str):
        intent = BackendClient.post_intent(new_intent)
        BackendClient.post_training_instance(message, intent.uuid)
