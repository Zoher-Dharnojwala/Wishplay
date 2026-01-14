# ai_service/screening_voice_flow.py
import os, uuid, logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from transformers import pipeline
from elevenlabs import ElevenLabs
import google.generativeai as genai
from fastapi.responses import FileResponse

router = APIRouter(prefix="/screening", tags=["Screening Voice Flow"])

BASE_DIR = os.path.join(os.path.dirname(__file__), "storage", "screening")
INPUT_DIR = os.path.join(BASE_DIR, "input")
TTS_DIR = os.path.join(BASE_DIR, "tts")
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(TTS_DIR, exist_ok=True)

ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")
client = ElevenLabs(api_key=ELEVEN_API_KEY)
genai.configure(api_key=GEMINI_KEY)

asr_model = pipeline("automatic-speech-recognition", model="openai/whisper-tiny", device=-1)
emotion_model = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", device=-1)

@router.post("/analyze")
async def screening(audio: UploadFile = File(...)):
    """Analyzes a short voice clip for emotional screening."""
    try:
        input_path = os.path.join(INPUT_DIR, f"in_{uuid.uuid4().hex}.wav")
        with open(input_path, "wb") as f:
            f.write(await audio.read())

        text = asr_model(input_path)["text"].strip()
        emotion = emotion_model(text)[0]["label"].lower()

        model = genai.GenerativeModel("models/gemini-2.0-pro")
        prompt = f"The person said '{text}' and seems {emotion}. Summarize their mood in one sentence."
        summary = model.generate_content(prompt).text.strip()

        # TTS response
        audio_stream = client.text_to_speech.convert(
            voice_id="EXAVITQu4vr4xnSDxMaL",
            model_id="eleven_multilingual_v2",
            text=summary
        )
        out_path = os.path.join(TTS_DIR, f"screen_{uuid.uuid4().hex}.mp3")
        with open(out_path, "wb") as f:
            for chunk in audio_stream:
                if isinstance(chunk, bytes):
                    f.write(chunk)

        return {
            "transcript": text,
            "emotion": emotion,
            "summary": summary,
            "audio_url": f"http://127.0.0.1:8000/storage/screening/tts/{os.path.basename(out_path)}"
        }

    except Exception as e:
        logging.error(f"Screening flow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
