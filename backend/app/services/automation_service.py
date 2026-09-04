import json
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.entities import AuditEvent


class AutomationService:
    def emit(
        self,
        db: Session,
        session_id: str,
        event_type: str,
        payload: dict | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            id=str(uuid4()),
            session_id=session_id,
            event_type=event_type,
            payload=json.dumps(payload or {}, ensure_ascii=False),
        )
        db.add(event)
        return event
