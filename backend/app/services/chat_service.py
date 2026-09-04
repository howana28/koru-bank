import json
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.router import HybridIntentRouter
from app.core.config import Settings
from app.models.entities import Conversation, DemoSession, Message
from app.schemas.chat import ChatResponse
from app.services.automation_service import AutomationService
from app.services.intents import IntentResult


class ConversationNotFoundError(Exception):
    pass


def clean_name(value: str) -> str | None:
    value = " ".join(value.strip().split())
    if not 2 <= len(value) <= 50:
        return None
    if not all(char.isalpha() or char in " -'" for char in value):
        return None
    return value.title()


class ChatService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.router = HybridIntentRouter(settings)
        self.automations = AutomationService()

    def _get_session(self, db: Session, session_id: str) -> DemoSession:
        record = db.get(DemoSession, session_id)
        if not record:
            raise ConversationNotFoundError("Sessão não encontrada. Inicie uma nova demonstração.")
        return record

    def _get_or_create_conversation(self, db: Session, session_id: str) -> Conversation:
        self._get_session(db, session_id)
        conversation = db.scalar(select(Conversation).where(Conversation.session_id == session_id))
        if conversation:
            return conversation
        conversation = Conversation(id=str(uuid4()), session_id=session_id, state="new")
        db.add(conversation)
        db.flush()
        return conversation

    def _record_message(
        self,
        db: Session,
        conversation: Conversation,
        role: str,
        content: str,
        intent: IntentResult | None = None,
    ) -> None:
        db.add(
            Message(
                id=str(uuid4()),
                conversation_id=conversation.id,
                role=role,
                content=content,
                intent=intent.intent if intent else None,
                confidence=intent.confidence if intent else None,
            )
        )

    def start(self, db: Session, session_id: str) -> ChatResponse:
        conversation = self._get_or_create_conversation(db, session_id)

        if conversation.state == "new":
            conversation.state = "ask_name"
            message = "Olá! Eu sou o assistente Koru. Como posso te chamar?"
            self._record_message(db, conversation, "assistant", message)
            db.commit()
            return ChatResponse(message=message, state=conversation.state, suggestions=[])

        message = self._resume_message(conversation)
        return ChatResponse(message=message, state=conversation.state, suggestions=self._suggestions(conversation.state))

    def respond(self, db: Session, session_id: str, text: str) -> ChatResponse:
        conversation = self._get_or_create_conversation(db, session_id)
        clean_text = text.strip()

        if conversation.state == "ended":
            return ChatResponse(
                message="Esta conversa foi encerrada. Inicie uma nova demonstração para continuar.",
                state="ended",
                suggestions=[],
            )

        if conversation.state == "ask_name":
            self._record_message(db, conversation, "user", clean_text)
            name = clean_name(clean_text)
            if not name:
                response = "Use apenas seu primeiro nome ou um nome fictício, sem números ou símbolos especiais."
                self._record_message(db, conversation, "assistant", response)
                db.commit()
                return ChatResponse(message=response, state=conversation.state, suggestions=[])

            conversation.user_name = name
            conversation.state = "mode_choice"
            response = f"Prazer, {name}! Nesta demonstração, você já é cliente ou quer conhecer o fluxo de abertura de conta?"
            self._record_message(db, conversation, "assistant", response)
            db.commit()
            return ChatResponse(
                message=response,
                state=conversation.state,
                suggestions=["Já sou cliente", "Quero virar cliente", "Sair"],
            )

        intent = self.router.classify(clean_text)
        self._record_message(db, conversation, "user", clean_text, intent)

        if intent.intent == "exit":
            conversation.state = "ended"
            response = "Demonstração encerrada. Obrigado por conhecer o Koru Bank."
            self._record_message(db, conversation, "assistant", response)
            db.commit()
            return ChatResponse(message=response, state="ended", intent=intent.intent, confidence=intent.confidence)

        if intent.intent == "menu":
            conversation.state = "mode_choice"
            conversation.pending_payload = None
            response = "Voltamos ao menu inicial. Você já é cliente ou quer conhecer o fluxo de abertura de conta?"
            self._record_message(db, conversation, "assistant", response)
            db.commit()
            return ChatResponse(
                message=response,
                state=conversation.state,
                intent=intent.intent,
                confidence=intent.confidence,
                suggestions=["Já sou cliente", "Quero virar cliente", "Sair"],
            )

        handler = getattr(self, f"_handle_{conversation.state}", self._handle_unknown_state)
        response = handler(db, conversation, intent)
        self._record_message(db, conversation, "assistant", response.message)
        db.commit()
        return response

    def _handle_mode_choice(self, db: Session, conversation: Conversation, intent: IntentResult) -> ChatResponse:
        event = None
        if intent.intent == "existing_client":
            conversation.state = "client_menu"
            message = "Perfeito. O que você quer simular agora?"
        elif intent.intent == "become_client":
            conversation.state = "new_client_demo"
            event = self.automations.emit(
                db,
                conversation.session_id,
                "lead_captured",
                {"source": "chat", "mode": "demo"},
            )
            message = (
                "Interesse registrado na simulação. Em um produto real, o próximo passo seria um fluxo seguro de onboarding/KYC. "
                "Aqui não vamos solicitar outros dados pessoais."
            )
        else:
            message = "Não consegui identificar essa opção. Escolha uma das alternativas abaixo."

        return ChatResponse(
            message=message,
            state=conversation.state,
            intent=intent.intent,
            confidence=intent.confidence,
            suggestions=self._suggestions(conversation.state),
            automation_event=event.event_type if event else None,
        )

    def _handle_client_menu(self, db: Session, conversation: Conversation, intent: IntentResult) -> ChatResponse:
        event = None
        if intent.intent == "balance":
            message = f"Seu saldo demonstrativo é de R$ {self._money(self.settings.demo_balance)}."
        elif intent.intent == "transfer":
            if "amount" in intent.entities and "recipient" in intent.entities:
                return self._prepare_transfer(db, conversation, intent)
            conversation.state = "transfer_capture"
            message = "Informe valor e destinatário. Exemplo: transferir 200 para Maria."
        elif intent.intent == "human_handoff":
            event = self.automations.emit(
                db,
                conversation.session_id,
                "handoff_requested",
                {"reason": "user_request"},
            )
            message = "Solicitação de atendimento humano registrada na simulação. Um sistema real encaminharia a conversa para a fila apropriada."
        else:
            message = "Posso consultar o saldo fictício, simular uma transferência ou registrar um handoff humano."

        return ChatResponse(
            message=message,
            state=conversation.state,
            intent=intent.intent,
            confidence=intent.confidence,
            suggestions=self._suggestions(conversation.state),
            automation_event=event.event_type if event else None,
        )

    def _handle_transfer_capture(self, db: Session, conversation: Conversation, intent: IntentResult) -> ChatResponse:
        if intent.intent != "transfer" or "amount" not in intent.entities or "recipient" not in intent.entities:
            return ChatResponse(
                message="Ainda preciso de valor e destinatário. Exemplo: transferir 200 para Maria.",
                state=conversation.state,
                intent=intent.intent,
                confidence=intent.confidence,
                suggestions=["Transferir 200 para Maria", "Menu"],
            )
        return self._prepare_transfer(db, conversation, intent)

    def _prepare_transfer(self, db: Session, conversation: Conversation, intent: IntentResult) -> ChatResponse:
        amount = Decimal(str(intent.entities["amount"]))
        recipient = str(intent.entities["recipient"])

        if amount > self.settings.high_value_transfer_limit:
            conversation.state = "client_menu"
            conversation.pending_payload = None
            event = self.automations.emit(
                db,
                conversation.session_id,
                "high_value_transfer_review",
                {"amount": float(amount), "recipient": recipient},
            )
            return ChatResponse(
                message=(
                    f"A simulação identificou R$ {self._money(amount)} como operação de alto valor. "
                    "Em vez de prosseguir automaticamente, o fluxo foi encaminhado para revisão manual."
                ),
                state=conversation.state,
                intent=intent.intent,
                confidence=intent.confidence,
                suggestions=self._suggestions(conversation.state),
                automation_event=event.event_type,
            )

        conversation.pending_payload = json.dumps({"amount": float(amount), "recipient": recipient}, ensure_ascii=False)
        conversation.state = "transfer_confirmation"
        return ChatResponse(
            message=f"Confirme a transferência simulada de R$ {self._money(amount)} para {recipient}. Nenhum valor real será movimentado.",
            state=conversation.state,
            intent=intent.intent,
            confidence=intent.confidence,
            suggestions=["Confirmar", "Cancelar"],
        )

    def _handle_transfer_confirmation(self, db: Session, conversation: Conversation, intent: IntentResult) -> ChatResponse:
        payload = json.loads(conversation.pending_payload or "{}")
        if intent.intent == "confirm" and payload:
            event = self.automations.emit(db, conversation.session_id, "transfer_simulated", payload)
            conversation.pending_payload = None
            conversation.state = "client_menu"
            return ChatResponse(
                message="Transferência simulada concluída e registrada na trilha de auditoria.",
                state=conversation.state,
                intent=intent.intent,
                confidence=intent.confidence,
                suggestions=self._suggestions(conversation.state),
                automation_event=event.event_type,
            )
        if intent.intent == "cancel":
            conversation.pending_payload = None
            conversation.state = "client_menu"
            return ChatResponse(
                message="Transferência cancelada. Nenhuma operação foi registrada como concluída.",
                state=conversation.state,
                intent=intent.intent,
                confidence=intent.confidence,
                suggestions=self._suggestions(conversation.state),
            )
        return ChatResponse(
            message="Para este passo, escolha Confirmar ou Cancelar.",
            state=conversation.state,
            intent=intent.intent,
            confidence=intent.confidence,
            suggestions=["Confirmar", "Cancelar"],
        )

    def _handle_new_client_demo(self, db: Session, conversation: Conversation, intent: IntentResult) -> ChatResponse:
        if intent.intent == "existing_client":
            conversation.state = "client_menu"
            message = "Tudo certo. Vamos para o menu de cliente da demonstração."
        else:
            message = "O fluxo de onboarding termina aqui para evitar coleta de dados reais. Você pode voltar ao menu e explorar o atendimento."
        return ChatResponse(
            message=message,
            state=conversation.state,
            intent=intent.intent,
            confidence=intent.confidence,
            suggestions=self._suggestions(conversation.state),
        )

    def _handle_unknown_state(self, db: Session, conversation: Conversation, intent: IntentResult) -> ChatResponse:
        conversation.state = "mode_choice"
        conversation.pending_payload = None
        return ChatResponse(
            message="O estado da conversa foi recuperado com segurança. Escolha como deseja continuar.",
            state=conversation.state,
            intent=intent.intent,
            confidence=intent.confidence,
            suggestions=self._suggestions(conversation.state),
        )

    def _resume_message(self, conversation: Conversation) -> str:
        messages = {
            "ask_name": "Retomamos sua sessão. Como posso te chamar?",
            "mode_choice": "Retomamos sua sessão. Você já é cliente ou quer conhecer o fluxo de abertura de conta?",
            "client_menu": "Retomamos sua sessão. Posso consultar saldo, simular transferência ou registrar atendimento humano.",
            "transfer_capture": "Retomamos sua transferência. Informe valor e destinatário.",
            "transfer_confirmation": "Há uma transferência simulada aguardando confirmação.",
            "new_client_demo": "O interesse no fluxo de abertura já foi registrado nesta demonstração.",
            "ended": "Esta conversa já foi encerrada.",
        }
        return messages.get(conversation.state, "Sessão recuperada.")

    @staticmethod
    def _suggestions(state: str) -> list[str]:
        return {
            "mode_choice": ["Já sou cliente", "Quero virar cliente", "Sair"],
            "client_menu": ["Consultar saldo", "Transferir 200 para Maria", "Falar com atendente"],
            "transfer_capture": ["Transferir 200 para Maria", "Menu"],
            "transfer_confirmation": ["Confirmar", "Cancelar"],
            "new_client_demo": ["Menu", "Sair"],
        }.get(state, [])

    @staticmethod
    def _money(value: Decimal) -> str:
        formatted = f"{value:,.2f}"
        return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
