from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.database import get_db
from app.models.entities import AuditEvent, Conversation, DemoSession, Message
from app.schemas.chat import ChatMessageRequest, ChatResponse, ChatStartRequest
from app.schemas.operations import DashboardResponse, RecentEvent
from app.schemas.session import SessionCreateRequest, SessionCreateResponse
from app.services.automation_service import AutomationService
from app.services.chat_service import ChatService, ConversationNotFoundError
from app.services.cpf import hash_cpf, is_valid_cpf, mask_cpf

router = APIRouter(prefix="/api/v1")
settings = get_settings()
chat_service = ChatService(settings)
automations = AutomationService()


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "ai_enabled": settings.ai_enabled,
        "intent_engine": "hybrid-ready/rules-active",
    }


@router.post("/sessions", response_model=SessionCreateResponse, status_code=201)
def create_session(payload: SessionCreateRequest, db: Session = Depends(get_db)) -> SessionCreateResponse:
    if not is_valid_cpf(payload.cpf):
        raise HTTPException(status_code=422, detail="CPF inválido para a demonstração.")

    session_id = str(uuid4())
    record = DemoSession(
        id=session_id,
        cpf_hash=hash_cpf(payload.cpf, settings.app_secret),
        masked_cpf=mask_cpf(payload.cpf),
    )
    db.add(record)
    automations.emit(db, session_id, "session_created", {"environment": settings.app_env})
    db.commit()

    return SessionCreateResponse(
        session_id=session_id,
        masked_cpf=record.masked_cpf,
        message="Sessão demonstrativa criada.",
    )


@router.post("/chat/start", response_model=ChatResponse)
def start_chat(payload: ChatStartRequest, db: Session = Depends(get_db)) -> ChatResponse:
    try:
        return chat_service.start(db, payload.session_id)
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/chat/messages", response_model=ChatResponse)
def post_message(payload: ChatMessageRequest, db: Session = Depends(get_db)) -> ChatResponse:
    try:
        return chat_service.respond(db, payload.session_id, payload.message)
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/operations/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db)) -> DashboardResponse:
    total_sessions = db.scalar(select(func.count()).select_from(DemoSession)) or 0
    active_conversations = db.scalar(
        select(func.count()).select_from(Conversation).where(Conversation.state != "ended")
    ) or 0
    total_messages = db.scalar(select(func.count()).select_from(Message)) or 0
    automation_events = db.scalar(
        select(func.count()).select_from(AuditEvent).where(AuditEvent.event_type != "session_created")
    ) or 0
    handoffs = db.scalar(
        select(func.count()).select_from(AuditEvent).where(AuditEvent.event_type == "handoff_requested")
    ) or 0
    avg_confidence = db.scalar(
        select(func.avg(Message.confidence)).where(Message.confidence.is_not(None))
    ) or 0.0

    state_rows = db.execute(select(Conversation.state, func.count()).group_by(Conversation.state)).all()
    states = {state: count for state, count in state_rows}

    recent = db.scalars(select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(8)).all()
    recent_events = [
        RecentEvent(
            id=event.id,
            session_id=event.session_id,
            event_type=event.event_type,
            created_at=event.created_at,
        )
        for event in recent
    ]

    return DashboardResponse(
        total_sessions=total_sessions,
        active_conversations=active_conversations,
        total_messages=total_messages,
        automation_events=automation_events,
        handoffs=handoffs,
        avg_intent_confidence=float(avg_confidence),
        states=states,
        recent_events=recent_events,
    )
