# ai_service/flows/next_question_flow.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import openai, os

router = APIRouter(prefix="/next-question", tags=["AI Conversation Flow"])

openai.api_key = os.getenv("OPENAI_API_KEY")

class SessionData(BaseModel):
    summary: str
    emotion: str
    sentiment: str
    context: str

class NextQuestionRequest(BaseModel):
    session_data: SessionData

@router.post("/")
async def generate_next_question(request: NextQuestionRequest):
    """Generate the next reflective question based on patient’s emotional session data."""
    try:
        content = f"""
        The patient reflected with the following context:
        - Summary: {request.session_data.summary}
        - Emotion: {request.session_data.emotion}
        - Sentiment: {request.session_data.sentiment}
        - Context: {request.session_data.context}

        Based on this, generate a compassionate follow-up question to encourage deeper reflection.
        """

        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a warm, emotionally intelligent therapeutic AI companion."},
                {"role": "user", "content": content}
            ]
        )
        return {"next_question": completion["choices"][0]["message"]["content"].strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
