import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import conversation_service as cs
from app.services.chat_service import generate_reply

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


class ChatRequest(BaseModel):
    conversation_id: uuid.UUID | None = None
    message: str = Field(min_length=1, max_length=8000)


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    reply: str


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    updated_at: datetime


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role: str
    content: str
    created_at: datetime


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    user = cs.get_or_create_dev_user(db)

    if req.conversation_id:
        conv = cs.get_conversation(db, req.conversation_id, user.id)
        if conv is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv = cs.create_conversation(db, user.id, title=req.message[:50])

    cs.save_message(db, conv.id, "user", req.message)
    history = cs.get_recent_messages(db, conv.id, limit=30)

    try:
        reply = generate_reply(history, user.name, user.timezone)
    except Exception:
        logger.exception("LLM call failed")
        raise HTTPException(status_code=502, detail="The AI service failed. Try again.")

    cs.save_message(db, conv.id, "assistant", reply)
    return ChatResponse(conversation_id=conv.id, reply=reply)


@router.get("/conversations", response_model=list[ConversationOut])
def conversations(db: Session = Depends(get_db)):
    user = cs.get_or_create_dev_user(db)
    return cs.list_conversations(db, user.id)


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageOut])
def conversation_messages(conversation_id: uuid.UUID, db: Session = Depends(get_db)):
    user = cs.get_or_create_dev_user(db)
    conv = cs.get_conversation(db, conversation_id, user.id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return cs.get_messages(db, conv.id)