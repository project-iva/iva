import os
from typing import List

import requests as requests

from models.meal import Meal, ChosenMeal


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
        response = requests.post(f'{base_api_url}/meal-tracking-entries/', headers=headers, data=chosen_meal.to_json())
        response.raise_for_status()
