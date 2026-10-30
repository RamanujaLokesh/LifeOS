import uuid

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import Conversation, Message, User
# from backend.app import db

DEV_EMAIL ="remo@lifeos.local"

def get_or_create_dev_user(db:Session)->User:
    """Temporary single user until real authentication is added"""
    user = db.scalar(select(User).where(User.email == DEV_EMAIL))
    if user is None:
        user = User(email = DEV_EMAIL, name="Remo",timezone=settings.user_timezone)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def create_conversation(db:Session, user_id:uuid.UUID,title:str="New chat")->Conversation:
    conv = Conversation(user_id=user_id, title=title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv

def get_conversation(db:Session,conversation_id:uuid.UUID, user_id:uuid.UUID)->Conversation|None:
    # Ownership check lives here: a conversation is only returned if it belongs to this user.
    return db.scalar(
        select(Conversation).where(
            Conversation.id==conversation_id,Conversation.user_id==user_id
        )
    )

def list_conversations(db: Session, user_id: uuid.UUID) -> list[Conversation]:
    return list(
        db.scalars(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )
    )


def save_message(db: Session, conversation_id: uuid.UUID, role: str, content: str) -> Message:
    msg = Message(conversation_id=conversation_id, role=role, content=content)
    db.add(msg)
    conv = db.get(Conversation, conversation_id)
    conv.updated_at = func.now()
    db.commit()
    db.refresh(msg)
    return msg


def get_messages(db: Session, conversation_id: uuid.UUID) -> list[Message]:
    return list(
        db.scalars(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
    )


def get_recent_messages(db: Session, conversation_id: uuid.UUID, limit: int = 30) -> list[dict]:
    """Last `limit` messages, oldest first, as plain dicts for the prompt."""
    rows = list(
        db.scalars(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
    )
    rows.reverse()
    return [{"role": m.role, "content": m.content} for m in rows]