# ai_service/tts_service.py
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import FileResponse
from transformers import pipeline
from elevenlabs import ElevenLabs
import uuid, os, logging

router = APIRouter(prefix="/tts", tags=["Text-to-Speech"])

# =========================================================
# 🗂 STORAGE DIRECTORY
# =========================================================
BASE_DIR = os.path.join(os.path.dirname(__file__), "storage", "tts")
os.makedirs(BASE_DIR, exist_ok=True)

# =========================================================
# ⚙️ MODEL INITIALIZATION
# =========================================================
emotion_analyzer = pipeline(
    "sentiment-analysis",
    model="j-hartmann/emotion-english-distilroberta-base",
    device=-1
)

ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVEN_API_KEY:
    raise RuntimeError("Missing ELEVENLABS_API_KEY environment variable")

client = ElevenLabs(api_key=ELEVEN_API_KEY)

VOICE_MAP = {
    "joy": "EXAVITQu4vr4xnSDxMaL",
    "sadness": "pFZP5JQG7iQjIQuC4Bku",
    "anger": "bIHbv24MWmeRgasZH58o",
    "fear": "2EiwWnXFnvU5JabPnv8n",
    "neutral": "cgSgspJ2msm6clMCkdW9",
    "surprise": "SAz9YHcvj6GT2YYXdXww",
    "love": "XrExE9yKIg1WjnnlVkGX",
}

# =========================================================
# 🎙️ ROUTE — GENERATE TTS
# =========================================================
@router.post("")
async def generate_tts(payload: dict = Body(...)):
    text = payload.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Missing text input")

    try:
        logging.warning(f"🎤 TTS request → {text[:60]}...")

        emotion_result = emotion_analyzer(text)[0]
        emotion_label = emotion_result["label"].lower()
        confidence = float(emotion_result["score"])
        logging.warning(f"💬 Emotion: {emotion_label} ({confidence:.3f})")

        voice_id = VOICE_MAP.get(emotion_label, VOICE_MAP["neutral"])
        logging.warning(f"🎙️ Using ElevenLabs voice ID: {voice_id}")

        audio_stream = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            text=text
        )

        filename = f"tts_{uuid.uuid4().hex}.mp3"
        output_path = os.path.join(BASE_DIR, filename)

        with open(output_path, "wb") as f:
            for chunk in audio_stream:
                if isinstance(chunk, bytes):
                    f.write(chunk)

        logging.warning(f"✅ TTS saved → {output_path}")

        return FileResponse(
            output_path,
            media_type="audio/mpeg",
            filename=filename,
            headers={
                "X-Emotion": emotion_label,
                "X-Confidence": str(round(confidence, 3)),
            }
        )

    except Exception as e:
        logging.error(f"TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
