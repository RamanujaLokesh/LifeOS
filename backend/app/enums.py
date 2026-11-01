from enum import StrEnum


class MemoryCategory(StrEnum):
    PREFERENCE = "preference"
    FACT = "fact"
    PROJECT = "project"
    DECISION = "decision"
    GOAL = "goal"
    PERSON = "person"


class MemoryStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"


class MemorySource(StrEnum):
    CHAT = "chat"
    MANUAL = "manual"