# ai_service/flows/chat_flow.py
from fastapi import APIRouter
from pydantic import BaseModel
import openai
import os

router = APIRouter(prefix="/chat", tags=["Chat API"])

class ChatRequest(BaseModel):
    message: str

openai.api_key = os.getenv("OPENAI_API_KEY")

@router.post("/")
def chat_reflective(request: ChatRequest):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a compassionate reflective AI helping users explore life memories."},
                {"role": "user", "content": request.message},
            ]
        )
        reply = completion["choices"][0]["message"]["content"]
        return {"response": reply}
    except Exception as e:
        return {"error": str(e)}
