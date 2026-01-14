import os
import uuid
import json
import torch
import librosa
import soundfile as sf
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from transformers import pipeline
from elevenlabs import ElevenLabs
from gtts import gTTS  # Fallback TTS (Google)
import warnings

warnings.filterwarnings("ignore")

router = APIRouter()

# --- Initialize Models ---
device = "cpu"

# Whisper (Speech → Text)
asr = pipeline("automatic-speech-recognition", model="openai/whisper-tiny", device="cpu")

# Text Generation (Empathetic AI)
chat_model_name = "mistralai/Mistral-7B-Instruct-v0.2"
chat_pipe = pipeline(
    "text-generation",
    model=chat_model_name,
    device_map="auto",
    max_new_tokens=200,
    temperature=0.8,
    top_p=0.9
)

# Sentiment Analysis
sentiment_pipe = pipeline("sentiment-analysis", model="j-hartmann/emotion-english-distilroberta-base")

# ElevenLabs client
tts_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

MAX_DURATION = 30
SUPER_MEMORY_DIR = "/home/ubuntu/Mimir/supermemory"

# --- Voice selection based on sentiment ---
VOICE_MAP = {
    "joy": "Rachel",           # gentle & cheerful
    "love": "Charlotte",       # calm warmth
    "sadness": "Bella",        # soft and empathetic
    "anger": "Adam",           # firm but composed
    "fear": "Clyde",           # soothing tone
    "surprise": "Elli",        # curious, upbeat
    "neutral": "Sarah"         # default balanced
}


# --- Helper: Transcribe long audio safely ---
def transcribe_long_audio(file_path: str) -> str:
    try:
        audio, sr = librosa.load(file_path, sr=16000)
        duration = librosa.get_duration(y=audio, sr=sr)
        text_output = ""

        if duration <= MAX_DURATION:
            result = asr(file_path)
            return result["text"]

        # Split into 30s chunks
        for start in range(0, int(duration), MAX_DURATION):
            end = min(start + MAX_DURATION, int(duration))
            chunk = audio[start * sr:end * sr]
            temp_path = f"chunk_{uuid.uuid4().hex}.wav"
            sf.write(temp_path, chunk, sr)
            result = asr(temp_path)
            text_output += " " + result["text"]
            os.remove(temp_path)

        return text_output.strip()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")


# --- Helper: Save conversation memory ---
def save_to_supermemory(user_text: str, ai_reply: str, sentiment: str):
    try:
        os.makedirs(SUPER_MEMORY_DIR, exist_ok=True)
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_text": user_text,
            "ai_reply": ai_reply,
            "sentiment": sentiment
        }
        memory_path = os.path.join(SUPER_MEMORY_DIR, f"memory_{uuid.uuid4().hex}.json")
        with open(memory_path, "w") as f:
            json.dump(entry, f, indent=2)
        print(f"🧠 Memory saved: {memory_path}")
    except Exception as e:
        print(f"⚠️ Could not save memory: {e}")


# --- Main Endpoint ---
@router.post("/speech-to-speech-local")
async def speech_to_speech_local(audio: UploadFile = File(...)):
    """
    Speech → Text → Empathetic AI → Speech (returns human-like, sentiment-aware response)
    """
    try:
        input_path = f"input_{uuid.uuid4().hex}.wav"
        output_path = f"reply_{uuid.uuid4().hex}.mp3"

        # Save uploaded audio
        with open(input_path, "wb") as f:
            f.write(await audio.read())

        # 1️⃣ Transcribe user speech
        user_text = transcribe_long_audio(input_path)
        print(f"🗣️ User said: {user_text}")

        # 2️⃣ Detect sentiment
        sentiment_result = sentiment_pipe(user_text)[0]
        sentiment = sentiment_result["label"].lower()
        confidence = round(sentiment_result["score"], 2)
        print(f"💬 Detected sentiment: {sentiment} (confidence={confidence})")

        # Choose appropriate voice
        voice_choice = VOICE_MAP.get(sentiment, "Sarah")
        print(f"🎙️ Selected voice: {voice_choice}")

        # 3️⃣ Generate empathetic human-like AI response
        prompt = (
            f"Respond as a caring, emotionally intelligent companion. "
            f"Be warm, understanding, and supportive. "
            f"Do NOT repeat or restate what the user said. "
            f"Speak naturally, like a compassionate human friend.\n\n"
            f"User said: \"{user_text}\"\nAI reply:"
        )

        response = chat_pipe(prompt, max_new_tokens=220, temperature=0.85, top_p=0.9)
        ai_reply_raw = response[0]["generated_text"]
        ai_reply = ai_reply_raw.split("AI reply:")[-1].strip()

        # Cleanup: remove any unwanted meta lines
        bad_prefixes = ["You are", "User said", "AI reply", "As an AI"]
        for bp in bad_prefixes:
            if ai_reply.startswith(bp):
                ai_reply = ai_reply[len(bp):].strip(" :.-")

        print(f"🤖 Final AI reply: {ai_reply}")

        # 4️⃣ Text → Speech (Natural Human Voice)
        try:
            print(f"🎧 Generating speech with ElevenLabs voice '{voice_choice}'...")
            audio_stream = tts_client.text_to_speech.convert(
                voice_id=voice_choice,
                model_id="eleven_multilingual_v2",
                text=ai_reply
            )
            with open(output_path, "wb") as f:
                for chunk in audio_stream:
                    if isinstance(chunk, bytes):
                        f.write(chunk)
            print("✅ ElevenLabs TTS generated successfully.")

        except Exception as e:
            print(f"⚠️ ElevenLabs error ({e}) — switching to gTTS fallback.")
            tts = gTTS(text=ai_reply, lang="en")
            tts.save(output_path)
            print("✅ gTTS fallback TTS generated.")

        # 5️⃣ Save conversation in supermemory
        save_to_supermemory(user_text, ai_reply, sentiment)

        # Clean up input file
        os.remove(input_path)

        # 6️⃣ Return final human-like audio
        print("✅ Speech-to-speech completed successfully.")
        return FileResponse(output_path, media_type="audio/mpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech-to-speech failed: {e}")
