from dataclasses import dataclass

from uuid import UUID

from models.json_model import JsonDecodableModel


@dataclass
class Intent(JsonDecodableModel):
    uuid: UUID
    intent: str

    @classmethod
    def from_dict(cls, d):
        return cls(
            UUID(d.get('uuid')),
            d.get('intent')
        )
