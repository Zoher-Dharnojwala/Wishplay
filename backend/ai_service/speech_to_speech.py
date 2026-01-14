# ai_service/speech_to_speech.py
import os, uuid, logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from transformers import pipeline
from elevenlabs import ElevenLabs
import google.generativeai as genai
import soundfile as sf
import librosa
import subprocess

router = APIRouter(prefix="/speech", tags=["Speech-to-Speech"])

# =========================================================
# 🗂 STORAGE
# =========================================================
BASE_DIR = os.path.join(os.path.dirname(__file__), "storage", "speech_to_speech")
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================================================
# ⚙️ MODELS
# =========================================================
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")

if not ELEVEN_API_KEY:
    raise RuntimeError("Missing ELEVENLABS_API_KEY")
if not GEMINI_KEY:
    raise RuntimeError("Missing GOOGLE_API_KEY")

client = ElevenLabs(api_key=ELEVEN_API_KEY)
genai.configure(api_key=GEMINI_KEY)
asr_model = pipeline("automatic-speech-recognition", model="openai/whisper-tiny", device=-1)

# =========================================================
# 🎧 SPEECH → SPEECH
# =========================================================
@router.post("/talk")
async def speech_to_speech(audio: UploadFile = File(...)):
    """Takes a voice file, transcribes it, generates a human-like reply, and returns voice output."""
    try:
        input_path = os.path.join(INPUT_DIR, f"user_{uuid.uuid4().hex}.wav")
        with open(input_path, "wb") as f:
            f.write(await audio.read())

        # Convert to mono 16kHz WAV for Whisper
        temp_wav = input_path.replace(".wav", "_converted.wav")
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", temp_wav],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # Step 1 — Transcribe
        text = asr_model(temp_wav)["text"].strip()
        logging.info(f"🗣️ User said: {text}")

        # Step 2 — Generate response (Gemini)
        model = genai.GenerativeModel("models/gemini-2.0-pro")
        prompt = f"The person said: '{text}'. Reply warmly, naturally, and briefly."
        response = model.generate_content(prompt)
        ai_reply = response.text.strip()
        logging.info(f"💬 AI reply: {ai_reply}")

        # Step 3 — Convert reply to voice
        audio_stream = client.text_to_speech.convert(
            voice_id="EXAVITQu4vr4xnSDxMaL",
            model_id="eleven_multilingual_v2",
            text=ai_reply
        )

        output_path = os.path.join(OUTPUT_DIR, f"reply_{uuid.uuid4().hex}.mp3")
        with open(output_path, "wb") as f:
            for chunk in audio_stream:
                if isinstance(chunk, bytes):
                    f.write(chunk)

        return {
            "transcript": text,
            "ai_reply": ai_reply,
            "audio_file": output_path,
            "audio_url": f"http://127.0.0.1:8000/storage/speech_to_speech/output/{os.path.basename(output_path)}"
        }

    except Exception as e:
        logging.error(f"Speech-to-speech failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
