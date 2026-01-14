# ai_service/flows/sentiment_flow.py
from fastapi import APIRouter
from pydantic import BaseModel
from transformers import pipeline

router = APIRouter(prefix="/sentiment", tags=["Sentiment API"])

# Input model
class SentimentRequest(BaseModel):
    text: str

# Load Hugging Face sentiment model once
sentiment_analyzer = pipeline("sentiment-analysis")

@router.post("/predict")
def analyze_sentiment(request: SentimentRequest):
    """
    Run sentiment analysis on user input text.
    """
    result = sentiment_analyzer(request.text)[0]
    return {"sentiment": result["label"], "confidence": round(result["score"], 3)}
