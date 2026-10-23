import logging
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


from app.services.chat_service import generate_reply

logger  = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


class ChatMessage(BaseModel):
    role: Literal["user","assistant"]
    content: str = Field(min_length = 1, max_length = 8000)



class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length = 1, max_lenth = 8000)


class ChatResponse(BaseModel):
    reply: str



@router.post("/chat", response_model = ChatResponse)
def chat(req:ChatRequest):
    try:
        reply = generate_reply([m.model_dump() for m in req.messages])
    except Exception:
        logger.exception("LLM call failed")
        raise HTTPException(status_code=502, detail = "The AI servoce failed. Try again.")
    return ChatResponse(reply = reply)