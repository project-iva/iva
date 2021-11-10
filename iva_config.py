from dataclasses import dataclass


@dataclass
class IvaConfig:
    ask_user_to_confirm_intent_prediction: bool = True
