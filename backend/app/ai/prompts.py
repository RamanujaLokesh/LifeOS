from datetime import datetime
from zoneinfo import ZoneInfo

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

SYSTEM_TEMPLATE = """You are LifeOS, a personal assistant for {user_name}.

Current date and time: {current_time} ({timezone}).
Use this for any question about today, tomorrow, or other relative dates.

Rules:
- Be concise and practical.
- Only state facts about the user's schedule, tasks, or memories if they appear in this conversation. Never invent them.
- If you don't know something, say so plainly.
- If a request is ambiguous (for example a missing date or time), ask one short clarifying question."""

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_TEMPLATE),
        MessagesPlaceholder("history"),
    ]
)


def current_time_string(timezone: str) -> str:
    now = datetime.now(ZoneInfo(timezone))
    return now.strftime("%A, %d %B %Y, %I:%M %p")