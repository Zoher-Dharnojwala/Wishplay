import os
import io
import uuid
import json
import random
import torch
import logging
import librosa
import soundfile as sf
from datetime import datetime
from functools import lru_cache
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from transformers import pipeline
from elevenlabs import ElevenLabs
from gtts import gTTS
from pydub import AudioSegment

# ===== IMPORTS FROM OTHER MODULES =====
from ai_service.stt import transcribe_audio
from ai_service.emotion import get_emotion
from ai_service.sentiment import analyze_sentiment
from ai_service.profile_manager import add_reflection
from ai_service.agents import get_next_question

# =========================================================
# 🔧 SETUP
# =========================================================
router = APIRouter()

BASE_DIR = "/home/ubuntu/Mimir/ai_service/storage/screening"
API_BASE_URL = "https://api.wishplay.ca"
INPUT_DIR = os.path.join(BASE_DIR, "input")
TTS_DIR = os.path.join(BASE_DIR, "tts")
REPLY_DIR = os.path.join(BASE_DIR, "reply")
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(TTS_DIR, exist_ok=True)
os.makedirs(REPLY_DIR, exist_ok=True)

QUESTIONS_PATH = "/home/ubuntu/Mimir/ai_service/knowledge/screening_questions.json"
SUPER_MEMORY_DIR = "/home/ubuntu/Mimir/ai_service/supermemory/screening"
os.makedirs(SUPER_MEMORY_DIR, exist_ok=True)

MAX_DURATION = 30  # seconds
TTS_CLIENT = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# =========================================================
# 🧠 CACHED MODELS
# =========================================================
@lru_cache(maxsize=1)
def get_asr():
    logging.warning("🎧 Loading Whisper ASR model (lazy)...")
    device = 0 if torch.cuda.is_available() else -1
    return pipeline("automatic-speech-recognition", model="openai/whisper-tiny", device=device)

@lru_cache(maxsize=1)
def get_emotion_model():
    logging.warning("💬 Loading Emotion Detection model (lazy)...")
    return pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", device=-1)

@lru_cache(maxsize=1)
def get_chat_model():
    logging.warning("💭 Loading Phi-3-mini Chat model (lazy)...")
    device = 0 if torch.cuda.is_available() else -1
    return pipeline(
        "text-generation",
        model="microsoft/Phi-3-mini-4k-instruct",
        device=device,
        max_new_tokens=150,
        temperature=0.8,
        top_p=0.9
    )

# =========================================================
# 🔊 TTS GENERATOR
# =========================================================
def generate_voice(text, emotion=None):
    """Generate emotion-aware voice."""
    output_path = os.path.join(TTS_DIR, f"tts_{uuid.uuid4().hex}.mp3")
    voice_map = {
        "joy": "EXAVITQu4vr4xnSDxMaL",
        "happiness": "EXAVITQu4vr4xnSDxMaL",
        "nostalgia": "pMsXgVXv3BLzUgSXdLrk",
        "sadness": "ErXwobaYiN019PkySvjV",
        "stress": "ErXwobaYiN019PkySvjV",
        "neutral": "MF3mGyEYCl7XYWbV9V6O"
    }
    selected_voice = voice_map.get(emotion, "MF3mGyEYCl7XYWbV9V6O")

    try:
        audio_stream = TTS_CLIENT.text_to_speech.convert(
            voice_id=selected_voice,
            model_id="eleven_multilingual_v2",
            text=text
        )
        with open(output_path, "wb") as f:
            for chunk in audio_stream:
                if isinstance(chunk, bytes):
                    f.write(chunk)
        logging.info(f"✅ TTS saved → {output_path}")
        return output_path
    except Exception as e:
        logging.warning(f"⚠️ ElevenLabs failed ({e}) — fallback to gTTS.")
        tts = gTTS(text=text, lang="en")
        tts.save(output_path)
        return output_path

# =========================================================
# 🚀 ROUTE: START SCREENING
# =========================================================
@router.post("/screening/start")
async def start_screening(patient_id: str = Form(...)):
    """Start screening with the first question."""
    try:
        with open(QUESTIONS_PATH, "r") as f:
            questions = json.load(f)
        first = sorted(questions, key=lambda q: q["priority"])[0]
        question_id = first["id"]
        question_text = random.choice(first["prompt_variants"])
        audio_file = generate_voice(question_text)

        return {
            "patient_id": patient_id,
            "question_id": question_id,
            "question_text": question_text,
            "audio_file": audio_file,
            "audio_url": f"{API_BASE_URL}/storage/screening/tts/{os.path.basename(audio_file)}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start screening: {e}")

# =========================================================
# 🚀 ROUTE: SCREENING REPLY (MAIN FLOW)
# =========================================================
@router.post("/screening/reply")
async def screening_reply(
    patient_id: str = Form(...),
    question_id: str = Form(...),
    audio: UploadFile = File(...)
):
    """Receive patient's audio, transcribe, analyze emotion, and generate the next adaptive question."""
    try:
        # 1️⃣ Save audio
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{patient_id}_{question_id}_{timestamp}.wav"
        file_path = os.path.join(INPUT_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(await audio.read())
        file_url = f"{API_BASE_URL}/storage/screening/input/{filename}"

        # 2️⃣ Transcribe
        transcript_result = transcribe_audio(file_path)
        transcript = transcript_result if isinstance(transcript_result, str) else transcript_result.get("text", "")

        # 3️⃣ Analyze emotion & sentiment
        emotion = get_emotion(transcript)
        sentiment = analyze_sentiment(transcript)

        # 4️⃣ Save reflection memory
        add_reflection(patient_id, {
            "question_id": question_id,
            "transcript": transcript,
            "emotion": emotion,
            "sentiment": sentiment
        })

        # 5️⃣ Get adaptive next question
        next_q = get_next_question(patient_id, transcript, emotion)
        next_question_text = next_q.get("text", "Would you like to tell me more about that?")

        # 6️⃣ Generate TTS for next question
        next_audio_file = generate_voice(next_question_text, emotion)
        next_audio_url = f"{API_BASE_URL}/storage/screening/tts/{os.path.basename(next_audio_file)}"

        # 7️⃣ Respond with full structured data
        return {
            "message": "Processed successfully.",
            "patient_id": patient_id,
            "question_id": question_id,
            "transcript": transcript,
            "emotion": emotion,
            "sentiment": sentiment,
            "next_question": next_question_text,
            "next_question_audio": next_audio_url,
            "file_url": file_url
        }

    except Exception as e:
        logging.error(f"❌ Error in /screening/reply: {e}")
        raise HTTPException(status_code=500, detail=f"Error in screening reply: {e}")

# =========================================================
# 🎙️ RE-RECORD AUDIO
# =========================================================
@router.post("/screening/re_record")
async def re_record_audio(
    patient_id: str = Form(...),
    new_audio: UploadFile = File(...),
    replace_start: float = Form(...),
    replace_end: float = Form(...)
):
    """Replace part of the last audio, stitch, and save new version."""
    try:
        candidate_files = [
            os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR)
            if f.endswith((".wav", ".mp3")) and patient_id in f
        ]
        if not candidate_files:
            raise HTTPException(status_code=404, detail=f"No previous audio found for {patient_id}")

        old_audio_path = sorted(candidate_files, key=os.path.getmtime, reverse=True)[0]
        old_audio = AudioSegment.from_file(old_audio_path)
        temp_path = os.path.join(INPUT_DIR, f"temp_{uuid.uuid4().hex}_{new_audio.filename}")
        with open(temp_path, "wb") as f:
            f.write(await new_audio.read())

        new_segment = AudioSegment.from_file(temp_path)
        before = old_audio[:int(replace_start * 1000)]
        after = old_audio[int(replace_end * 1000):]
        stitched_audio = before + new_segment + after

        stitched_filename = f"{patient_id}_stitched_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
        stitched_path = os.path.join(REPLY_DIR, stitched_filename)
        stitched_audio.export(stitched_path, format="mp3")
        os.remove(temp_path)

        return {
            "message": "Audio successfully re-recorded and stitched.",
            "old_audio": old_audio_path,
            "new_audio": stitched_path,
            "audio_url": f"{API_BASE_URL}/storage/screening/reply/{os.path.basename(stitched_path)}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stitching audio: {e}")
