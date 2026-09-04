from app.services.intents import RuleIntentClassifier


classifier = RuleIntentClassifier()


def test_new_client_has_priority_over_generic_client_word():
    result = classifier.classify("quero ser cliente")
    assert result.intent == "become_client"


def test_existing_client():
    assert classifier.classify("já sou cliente").intent == "existing_client"


def test_transfer_extracts_entities():
    result = classifier.classify("quero transferir 200 para Maria")
    assert result.intent == "transfer"
    assert result.entities["amount"] == 200.0
    assert result.entities["recipient"] == "Maria"


def test_unknown_intent_is_low_confidence():
    result = classifier.classify("abacaxi azul")
    assert result.intent == "unknown"
    assert result.confidence < 0.5
