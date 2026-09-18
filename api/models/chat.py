from uuid import UUID
from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: UUID
    user_query: str

class ChatResponse(BaseModel):
    session_id: UUID
    new_messages: list[dict[str, str | list[dict[str, str | dict[str, str] | int]]]]