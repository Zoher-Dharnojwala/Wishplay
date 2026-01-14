# ai_service/flows/keywords_flow.py
from fastapi import APIRouter
from pydantic import BaseModel
from keybert import KeyBERT

router = APIRouter(prefix="/keywords", tags=["Keyword Extraction API"])

class KeywordRequest(BaseModel):
    text: str

kw_model = KeyBERT(model="all-MiniLM-L6-v2")

@router.post("/")
def extract_keywords(request: KeywordRequest):
    keywords = kw_model.extract_keywords(request.text, keyphrase_ngram_range=(1, 2), stop_words="english", top_n=5)
    formatted = [{"keyword": kw, "score": round(score, 3)} for kw, score in keywords]
    return {"keywords": formatted}
