# ai_service/flows/emotion_flow.py
from fastapi import APIRouter
from pydantic import BaseModel
from transformers import pipeline

router = APIRouter(prefix="/emotion", tags=["Emotion API"])

# Input model
class EmotionRequest(BaseModel):
    text: str

# Load Hugging Face emotion model
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=None)

@router.post("/analyze")
def analyze_emotion(request: EmotionRequest):
    """
    Detect dominant emotion and confidence scores.
    """
    results = emotion_classifier(request.text)
    emotions = {item["label"]: float(item["score"]) for item in results[0]}
    dominant = max(emotions, key=emotions.get)
    return {"dominant_emotion": dominant, "all_scores": emotions}
