from dataclasses import dataclass

from uuid import UUID

from models.json_model import JsonEncodableModel


@dataclass
class TrainingInstance(JsonEncodableModel):
    message_text: str
    intent: UUID
