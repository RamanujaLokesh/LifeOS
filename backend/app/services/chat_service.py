from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from app.ai.model import get_model


SYSTEM_PROMPT = "you are LifeOS, a concise and helpful personal assistant."


def to_langchain_messages(history: list[dict]) -> list[BaseMessage]:
    messages: list[BaseMessage] = [SystemMessage(content = SYSTEM_PROMPT)]
    for m in history:
        if m["role"] == "user":
            messages.append(HumanMessage(content = m["content"]))
        else:
            messages.append(AIMessage(content =m["content"]))
    return messages

def generate_reply(history: list[dict]) -> str:
    response = get_model().invoke(to_langchain_messages(history))
    return response.content