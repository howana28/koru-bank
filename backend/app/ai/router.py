from app.ai.base import IntentProvider
from app.core.config import Settings
from app.services.intents import IntentResult, RuleIntentClassifier


class DisabledAIProvider:
    def classify(self, text: str) -> IntentResult | None:
        return None


class HybridIntentRouter:
    """
    Rule-first router.

    AI is intentionally disabled in the portfolio baseline. When enabled later,
    a provider can be injected and used only for low-confidence/fallback cases.
    """

    def __init__(
        self,
        settings: Settings,
        rules: RuleIntentClassifier | None = None,
        ai_provider: IntentProvider | None = None,
    ) -> None:
        self.settings = settings
        self.rules = rules or RuleIntentClassifier()
        self.ai_provider = ai_provider or DisabledAIProvider()

    def classify(self, text: str) -> IntentResult:
        rule_result = self.rules.classify(text)
        if rule_result.intent != "unknown" or not self.settings.ai_enabled:
            return rule_result

        ai_result = self.ai_provider.classify(text)
        return ai_result or rule_result
