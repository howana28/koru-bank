from typing import Protocol

from app.services.intents import IntentResult


class IntentProvider(Protocol):
    """Contract for any future AI intent provider."""

    def classify(self, text: str) -> IntentResult | None:
        ...
