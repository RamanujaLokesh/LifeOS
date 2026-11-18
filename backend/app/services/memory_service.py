import logging
import re
import uuid
from difflib import SequenceMatcher

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai.extraction import extract_memory_candidates
from app.ai.schemas import MemoryCandidate
from app.db.models import Memory
from app.db.session import SessionLocal
from app.enums import MemorySource, MemoryStatus

logger = logging.getLogger(__name__)

MAX_PENDING = 50
SIMILARITY_THRESHOLD = 0.88

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\-]{10,}"),                                   # API-key-like
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{10,}"),                        # bearer tokens
    re.compile(r"\b(?:\d[ -]?){12,19}\b"),                                   # card / ID-number-like
    re.compile(r"(?i)\b(password|passwd|passcode|pin|api[ _-]?key|secret|token)\b\s*(is|=|:)"),
]


def normalize(text: str) -> str:
    text = re.sub(r"[^a-z0-9 ]+", "", text.lower())
    return " ".join(text.split())


def looks_like_secret(text: str) -> bool:
    return any(p.search(text) for p in SECRET_PATTERNS)


def is_duplicate(norm: str, existing_norms: list[str]) -> bool:
    return any(
        norm == e or SequenceMatcher(None, norm, e).ratio() >= SIMILARITY_THRESHOLD
        for e in existing_norms
    )


def save_candidates(
    db: Session,
    *,
    user_id: uuid.UUID,
    candidates: list[MemoryCandidate],
    source_message_id: uuid.UUID | None,
) -> list[Memory]:
    existing = db.scalars(select(Memory.content).where(Memory.user_id == user_id)).all()
    existing_norms = [normalize(c) for c in existing]
    pending_count = db.scalar(
        select(func.count())
        .select_from(Memory)
        .where(Memory.user_id == user_id, Memory.status == MemoryStatus.PENDING.value)
    )

    saved: list[Memory] = []
    for cand in candidates:
        if pending_count + len(saved) >= MAX_PENDING:
            break
        content = " ".join(cand.content.split())
        if looks_like_secret(content):
            logger.warning("Dropped a memory candidate that looked like a secret")
            continue
        norm = normalize(content)
        if is_duplicate(norm, existing_norms):
            continue
        mem = Memory(
            user_id=user_id,
            content=content,
            category=cand.category.value,
            status=MemoryStatus.PENDING.value,
            source=MemorySource.CHAT.value,
            source_message_id=source_message_id,
        )
        db.add(mem)
        saved.append(mem)
        existing_norms.append(norm)
    db.commit()
    return saved


def extract_and_store(
    user_id: uuid.UUID,
    messages: list[dict],
    source_message_id: uuid.UUID,
    tz: str,
) -> None:
    """Runs after the chat response has been sent, with its own DB session.
    The request's session is already closed by then. Must never raise."""
    try:
        candidates = extract_memory_candidates(messages, tz=tz)
        if not candidates:
            return
        with SessionLocal() as db:
            save_candidates(
                db, user_id=user_id, candidates=candidates, source_message_id=source_message_id
            )
    except Exception:
        logger.exception("Background memory extraction failed")


def list_memories(db: Session, *, user_id: uuid.UUID, status: str | None = None) -> list[Memory]:
    query = select(Memory).where(Memory.user_id == user_id)
    if status:
        query = query.where(Memory.status == status)
    return list(db.scalars(query.order_by(Memory.created_at.desc())))


def get_memory(db: Session, *, user_id: uuid.UUID, memory_id: uuid.UUID) -> Memory | None:
    return db.scalar(
        select(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
    )


def approve_memory(db: Session, *, user_id: uuid.UUID, memory_id: uuid.UUID) -> Memory | None:
    mem = get_memory(db, user_id=user_id, memory_id=memory_id)
    if mem is None:
        return None
    if mem.status != MemoryStatus.ACTIVE.value:
        mem.status = MemoryStatus.ACTIVE.value
        db.commit()
        db.refresh(mem)
    return mem


def delete_memory(db: Session, *, user_id: uuid.UUID, memory_id: uuid.UUID) -> bool:
    mem = get_memory(db, user_id=user_id, memory_id=memory_id)
    if mem is None:
        return False
    db.delete(mem)
    db.commit()
    return True