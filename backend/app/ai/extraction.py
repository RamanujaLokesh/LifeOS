import logging

from app.ai.model import get_model
from app.ai.prompts import current_time_string, extraction_prompt
from app.ai.schemas import MemoryCandidate, MemoryCandidateList

logger = logging.getLogger(__name__)


def format_transcript(messages: list[dict]) -> str:
    return "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)


def extract_memory_candidates(messages: list[dict], tz: str = "UTC") -> list[MemoryCandidate]:
    """Return memory candidates found in the conversation. Never raises:
    memory extraction must not be able to break the chat."""
    model = get_model(temperature=0).with_structured_output(
        MemoryCandidateList, method="function_calling"
    )
    chain = extraction_prompt | model
    try:
        result = chain.invoke(
            {
                "current_time": current_time_string(tz),
                "transcript": format_transcript(messages),
            }
        )
    except Exception:
        logger.exception("Memory extraction failed")
        return []
    return result.memories
