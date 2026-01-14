# ai_service/flows/voice_flow.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from transformers import pipeline
import tempfile

router = APIRouter(prefix="/voice", tags=["Voice Processing"])

@router.post("/")
async def transcribe_voice(file: UploadFile = File(...)):
    """Transcribe uploaded voice recording into text."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base")
        result = transcriber(tmp_path)

        return {"transcription": result["text"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
