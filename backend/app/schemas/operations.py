from datetime import datetime

from pydantic import BaseModel


class RecentEvent(BaseModel):
    id: str
    session_id: str
    event_type: str
    created_at: datetime


class DashboardResponse(BaseModel):
    total_sessions: int
    active_conversations: int
    total_messages: int
    automation_events: int
    handoffs: int
    avg_intent_confidence: float
    states: dict[str, int]
    recent_events: list[RecentEvent]
