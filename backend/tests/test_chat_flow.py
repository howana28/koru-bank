from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.database import Base
from app.models.entities import AuditEvent, DemoSession
from app.services.chat_service import ChatService


def make_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_chat_state_is_bound_to_session_and_transfer_is_confirmed():
    db = make_db()
    session_id = "11111111-1111-1111-1111-111111111111"
    db.add(DemoSession(id=session_id, cpf_hash="x" * 64, masked_cpf="***.***.***-25"))
    db.commit()

    service = ChatService(Settings())
    assert service.start(db, session_id).state == "ask_name"
    assert service.respond(db, session_id, "Ana").state == "mode_choice"
    assert service.respond(db, session_id, "Já sou cliente").state == "client_menu"

    transfer = service.respond(db, session_id, "transferir 200 para Maria")
    assert transfer.state == "transfer_confirmation"

    confirmed = service.respond(db, session_id, "confirmar")
    assert confirmed.state == "client_menu"
    assert confirmed.automation_event == "transfer_simulated"

    event = db.scalar(select(AuditEvent).where(AuditEvent.event_type == "transfer_simulated"))
    assert event is not None


def test_high_value_transfer_triggers_manual_review():
    db = make_db()
    session_id = "22222222-2222-2222-2222-222222222222"
    db.add(DemoSession(id=session_id, cpf_hash="y" * 64, masked_cpf="***.***.***-25"))
    db.commit()

    service = ChatService(Settings())
    service.start(db, session_id)
    service.respond(db, session_id, "Bia")
    service.respond(db, session_id, "Já sou cliente")
    response = service.respond(db, session_id, "transferir 6000 para Maria")

    assert response.state == "client_menu"
    assert response.automation_event == "high_value_transfer_review"
