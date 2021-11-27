from dataclasses import dataclass


@dataclass
class IvaConfig:
    ask_user_to_confirm_intent_prediction: bool = True
    ask_user_to_confirm_intent_prediction_for_confidence_lower_than: float = 1.0
