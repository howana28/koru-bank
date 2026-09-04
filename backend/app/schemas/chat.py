from pydantic import BaseModel, Field


class ChatStartRequest(BaseModel):
    session_id: str = Field(min_length=36, max_length=36)


class ChatMessageRequest(BaseModel):
    session_id: str = Field(min_length=36, max_length=36)
    message: str = Field(min_length=1, max_length=300)


class ChatResponse(BaseModel):
    message: str
    state: str
    intent: str | None = None
    confidence: float | None = None
    suggestions: list[str] = Field(default_factory=list)
    automation_event: str | None = None
