import os

from fastapi import HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm() -> ChatGoogleGenerativeAI:
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="AI is not set up: add GOOGLE_API_KEY to .env")
    return ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL", "gemini-flash-latest"), api_key=key)
