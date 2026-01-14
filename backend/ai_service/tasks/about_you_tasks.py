import os
import re
import uuid
import json
import random
import torch
import librosa
import soundfile as sf
import logging
from datetime import datetime
from functools import lru_cache
from crewai import Task
from fastapi import HTTPException
from transformers import pipeline
from elevenlabs import ElevenLabs
from gtts import gTTS
from ai_service.agents import legacy_curator  # ✅ Import the actual agent

# =========================================================
# 🗂 STORAGE
# =========================================================
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "storage", "about_you")
INPUT_DIR = os.path.join(BASE_DIR, "input")
REPLY_DIR = os.path.join(BASE_DIR, "reply")
TTS_DIR = os.path.join(BASE_DIR, "tts")

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(REPLY_DIR, exist_ok=True)
os.makedirs(TTS_DIR, exist_ok=True)

QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "about_you_questions.json")
SUPER_MEMORY_DIR = os.path.join(os.path.dirname(__file__), "..", "supermemory", "about_you")
MAX_DURATION = 30  # seconds

# =========================================================
# ⚙️ MODEL HELPERS
# =========================================================
@lru_cache(maxsize=1)
def get_asr():
    """Load Whisper ASR model"""
    device = 0 if torch.cuda.is_available() else -1
    return pipeline("automatic-speech-recognition", model="openai/whisper-tiny", device=device)

@lru_cache(maxsize=1)
def get_emotion_model():
    """Load emotion classification model"""
    return pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", device=-1)

@lru_cache(maxsize=1)
def get_chat_model():
    """Load Phi-3-mini text generation model"""
    device = 0 if torch.cuda.is_available() else -1
    return pipeline(
        "text-generation",
        model="microsoft/Phi-3-mini-4k-instruct",
        device=device,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        max_new_tokens=150,
        temperature=0.7,
        top_p=0.9
    )

tts_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# =========================================================
# 🎧 AUDIO UTILITIES
# =========================================================
def transcribe_audio(file_path: str) -> str:
    """Transcribe long audio files safely by splitting into chunks."""
    asr = get_asr()
    audio, sr = librosa.load(file_path, sr=16000)
    duration = librosa.get_duration(y=audio, sr=sr)

    if duration <= MAX_DURATION:
        return asr(file_path)["text"]

    text_output = ""
    for start in range(0, int(duration), MAX_DURATION):
        end = min(start + MAX_DURATION, int(duration))
        chunk = audio[start * sr:end * sr]
        temp = os.path.join(INPUT_DIR, f"chunk_{uuid.uuid4().hex}.wav")
        sf.write(temp, chunk, sr)
        text_output += " " + asr(temp)["text"]
        os.remove(temp)
    return text_output.strip()

# =========================================================
# 🧠 MEMORY
# =========================================================
def save_to_memory(question_id, question_text, user_text, emotion, ai_reply):
    """Save conversation entries for future recall."""
    os.makedirs(SUPER_MEMORY_DIR, exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "question_id": question_id,
        "question_text": question_text,
        "user_text": user_text,
        "emotion_detected": emotion,
        "ai_reply": ai_reply
    }
    path = os.path.join(SUPER_MEMORY_DIR, f"memory_{uuid.uuid4().hex}.json")
    with open(path, "w") as f:
        json.dump(entry, f, indent=2)
    logging.info(f"🧠 Memory saved → {path}")

# =========================================================
# 🔊 TTS
# =========================================================
def generate_voice(text, emotion=None):
    """Generate emotional voice output using ElevenLabs or gTTS fallback."""
    output_path = os.path.join(TTS_DIR, f"aboutyou_{uuid.uuid4().hex}.mp3")
    voice_map = {
        "joy": "EXAVITQu4vr4xnSDxMaL",
        "happiness": "EXAVITQu4vr4xnSDxMaL",
        "pride": "EXAVITQu4vr4xnSDxMaL",
        "nostalgia": "pMsXgVXv3BLzUgSXdLrk",
        "reflective": "pMsXgVXv3BLzUgSXdLrk",
        "sadness": "ErXwobaYiN019PkySvjV",
        "stress": "ErXwobaYiN019PkySvjV",
        "fear": "ErXwobaYiN019PkySvjV",
        "neutral": "MF3mGyEYCl7XYWbV9V6O",
        "trust": "MF3mGyEYCl7XYWbV9V6O"
    }
    selected = voice_map.get(emotion, "MF3mGyEYCl7XYWbV9V6O")

    try:
        stream = tts_client.text_to_speech.convert(
            voice_id=selected,
            model_id="eleven_multilingual_v2",
            text=text
        )
        with open(output_path, "wb") as f:
            for chunk in stream:
                if isinstance(chunk, bytes):
                    f.write(chunk)
        return output_path
    except Exception as e:
        logging.warning(f"⚠️ ElevenLabs failed ({e}), falling back to gTTS.")
        gTTS(text=text, lang="en").save(output_path)
        return output_path

# =========================================================
# 🧩 CREWAI TASK
# =========================================================
about_you_voice_task = Task(
    description="Handle the full voice-based About You question-answer step.",
    expected_output="Next question, AI reply, and generated audio file.",
    agent=legacy_curator,  # ✅ Fixed: use actual agent object
)

def execute_about_you_voice_task(question_id: str, audio_path: str):
    """Main logic previously handled by /reply endpoint."""
    try:
        # Load question data
        with open(QUESTIONS_PATH, "r") as f:
            questions = json.load(f)
        question = next((q for q in questions if q["id"] == question_id), None)
        if not question:
            raise HTTPException(status_code=404, detail="Invalid question ID.")

        question_text = random.choice(question["prompt_variants"])

        # Speech → Text → Emotion
        user_text = transcribe_audio(audio_path).strip()
        emotion = get_emotion_model()(user_text)[0]["label"].lower()

        # AI response
        followup = random.choice(question["followups"])
        prompt = (
            f"The person said: '{user_text}' and seems {emotion}. "
            "Respond warmly, compassionately, and naturally. Avoid robotic tone or instructions."
        )
        response = get_chat_model()(prompt)[0]["generated_text"]
        reply_clean = re.sub(r'^(The person said.*|Respond.*|Patient.*)', '', response, flags=re.I).strip()
        full_reply = f"{reply_clean}. {followup}".strip()

        # Save + generate audio
        save_to_memory(question_id, question_text, user_text, emotion, full_reply)
        ai_audio = generate_voice(full_reply, emotion=emotion)

        # Get next question
        next_q = next((q for q in questions if q["priority"] > question["priority"]), None)
        if next_q:
            next_text = random.choice(next_q["prompt_variants"])
            next_audio = generate_voice(next_text, emotion="neutral")
            return {
                "ai_reply": full_reply,
                "emotion": emotion,
                "ai_audio": ai_audio,
                "next_question_id": next_q["id"],
                "next_question_text": next_text,
                "next_question_audio": next_audio
            }

        # No more questions
        return {
            "ai_reply": full_reply,
            "emotion": emotion,
            "ai_audio": ai_audio,
            "message": "All questions in 'About You' section completed."
        }

    except Exception as e:
        logging.error(f"❌ AboutYou task error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
