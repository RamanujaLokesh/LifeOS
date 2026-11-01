from pydantic import BaseModel, Field

from app.enums import MemoryCategory


class MemoryCandidate(BaseModel):
    """One durable fact about the user that is worth remembering."""

    content: str = Field(
        min_length=5,
        max_length=300,
        description=(
            "One short, self-contained statement starting with 'The user', "
            "for example: 'The user chose PostgreSQL for LifeOS.' "
            "It must make sense without the surrounding conversation."
        ),
    )
    category: MemoryCategory = Field(
        description=(
            "preference: likes, dislikes, how they want things done. "
            "fact: stable personal facts such as role or location. "
            "project: what they are building or working on. "
            "decision: a choice they have made. "
            "goal: something they want to achieve. "
            "person: a person in their life and the relationship."
        )
    )


class MemoryCandidateList(BaseModel):
    """All memory candidates found in a conversation. Empty if there are none."""

    memories: list[MemoryCandidate] = Field(default_factory=list)