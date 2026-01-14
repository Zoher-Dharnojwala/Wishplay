# ai_service/flows/summarize_flow.py
from fastapi import APIRouter
from pydantic import BaseModel
from transformers import pipeline

router = APIRouter(prefix="/summarize", tags=["Summarization API"])

class SummarizeRequest(BaseModel):
    text: str

# Load summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@router.post("/")
def summarize_text(request: SummarizeRequest):
    summary = summarizer(request.text, max_length=100, min_length=25, do_sample=False)
    return {"summary": summary[0]["summary_text"]}
