from pydantic import BaseModel, Field


class SessionCreateRequest(BaseModel):
    cpf: str = Field(min_length=11, max_length=20)


class SessionCreateResponse(BaseModel):
    session_id: str
    masked_cpf: str
    message: str
