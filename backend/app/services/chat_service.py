from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from app.ai.model import get_model
from app.ai.prompts import chat_prompt, current_time_string
from app.config import settings

USER_NAME = "Remo"

# SYSTEM_PROMPT = "you are LifeOS, a concise and helpful personal assistant."


def to_langchain_messages(history: list[dict]) -> list[BaseMessage]:
    messages: list[BaseMessage] = []
    for m in history:
        if m["role"] == "user":
            messages.append(HumanMessage(content = m["content"]))
        else:
            messages.append(AIMessage(content =m["content"]))
    return messages


def build_prompt_messages(history: list[dict])-> list[BaseMessage]:
    prompt_value = chat_prompt.invoke(
        {
            "user_name": USER_NAME,
            "current_time": current_time_string(settings.user_timezone),
            "timezone":settings.user_timezone,
            "history":to_langchain_messages(history),
        }
    )
    return prompt_value.to_messages()


def generate_reply(history: list[dict]) -> str:
    messages = build_prompt_messages(history)
    response = get_model().invoke(messages)
    return response.content

