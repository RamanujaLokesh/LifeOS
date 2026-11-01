from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, SystemMessage
from app.ai.model import get_model
from app.api.chat import router as chat_router
from app.api.auth import router as auth_router

app = FastAPI(title="LifeOS")
app.include_router(auth_router)
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/debug/ask")
def debug_ask(q: str):
    messages = [
        SystemMessage(content="You are LifeOS, a concise personal assistant."),
        HumanMessage(content=q),
    ]
    response = get_model().invoke(messages)
    return {"answer": response.content}