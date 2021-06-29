from dataclasses import dataclass
from typing import List

from json_model import JsonModel


@dataclass
class MealIngredient(JsonModel):
    ingredient_name: str
    amount: float
    kcal: float

    @classmethod
    def from_dict(cls, d):
        return cls(
            d.get('ingredient_name'),
            d.get('amount'),
            d.get('kcal'),
        )


@dataclass
class Meal(JsonModel):
    id: int
    name: str
    type: str
    kcal: float
    ingredients: List[MealIngredient]

    @classmethod
    def from_dict(cls, d):
        ingredients = d.get('ingredients')
        return cls(
            d.get('id'),
            d.get('name'),
            d.get('type'),
            d.get('kcal'),
            [MealIngredient.from_dict(ingredients_dict) for ingredients_dict in ingredients]
        )


@dataclass
class ChosenMeal(JsonModel):
    meal: int

    @classmethod
    def from_dict(cls, d):
        return cls(
            d.get('meal')
        )
