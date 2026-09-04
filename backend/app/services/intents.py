import re
import unicodedata
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class IntentResult:
    intent: str
    confidence: float
    entities: dict[str, str | float] = field(default_factory=dict)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower().strip())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", text)


def parse_transfer(text: str) -> dict[str, str | float]:
    normalized = normalize(text)
    amount_match = re.search(r"(?:r\$\s*)?(\d+(?:[.,]\d{1,2})?)", normalized)
    recipient_match = re.search(r"\bpara\s+([a-z][a-z\s'-]{1,50})", normalized)

    entities: dict[str, str | float] = {}
    if amount_match:
        try:
            amount = Decimal(amount_match.group(1).replace(",", "."))
            if amount > 0:
                entities["amount"] = float(amount)
        except InvalidOperation:
            pass
    if recipient_match:
        recipient = recipient_match.group(1).strip(" .,-")
        if recipient:
            entities["recipient"] = recipient.title()
    return entities


class RuleIntentClassifier:
    """Deterministic classifier kept independent from the conversation FSM."""

    def classify(self, text: str) -> IntentResult:
        message = normalize(text)

        if message in {"3", "sair", "encerrar", "tchau", "finalizar"} or "sair do chat" in message:
            return IntentResult("exit", 0.99)

        if message in {"menu", "voltar", "inicio"}:
            return IntentResult("menu", 0.99)

        # Specific new-client patterns must be evaluated BEFORE the generic word "cliente".
        new_client_patterns = (
            "quero virar cliente",
            "quero ser cliente",
            "abrir conta",
            "nova conta",
            "nao sou cliente",
        )
        if message == "2" or any(pattern in message for pattern in new_client_patterns):
            return IntentResult("become_client", 0.96)

        existing_client_patterns = ("ja sou cliente", "sou cliente", "tenho conta")
        if message == "1" or any(pattern in message for pattern in existing_client_patterns):
            return IntentResult("existing_client", 0.96)

        if "saldo" in message or "quanto tenho" in message:
            return IntentResult("balance", 0.95)

        if any(term in message for term in ("transfer", "pix", "enviar dinheiro", "mandar dinheiro")):
            return IntentResult("transfer", 0.94, parse_transfer(message))

        if any(term in message for term in ("atendente", "humano", "pessoa", "falar com alguem")):
            return IntentResult("human_handoff", 0.94)

        if message in {"sim", "confirmar", "confirmo", "pode confirmar"}:
            return IntentResult("confirm", 0.99)

        if message in {"nao", "não", "cancelar", "cancela"}:
            return IntentResult("cancel", 0.99)

        return IntentResult("unknown", 0.35)
