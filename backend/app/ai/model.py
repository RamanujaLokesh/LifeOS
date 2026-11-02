from langchain_openai import ChatOpenAI
from app.config import settings

def get_model(temperature: float = 0.2) -> ChatOpenAI:
    return ChatOpenAI(
        model = settings.model_name,
        api_key = settings.openai_api_key,
        temperature = temperature,
    )