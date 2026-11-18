import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.enums import MemoryStatus
from app.services import memory_service as ms

router = APIRouter(prefix="/api/memories")


class MemoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    content: str
    category: str
    status: str
    source: str
    source_message_id: uuid.UUID | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=list[MemoryOut])
def list_memories(
    status: MemoryStatus | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return ms.list_memories(db, user_id=user.id, status=status.value if status else None)


@router.post("/{memory_id}/approve", response_model=MemoryOut)
def approve_memory(
    memory_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    mem = ms.approve_memory(db, user_id=user.id, memory_id=memory_id)
    if mem is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return mem


@router.delete("/{memory_id}", status_code=204)
def delete_memory(
    memory_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not ms.delete_memory(db, user_id=user.id, memory_id=memory_id):
        raise HTTPException(status_code=404, detail="Memory not found")