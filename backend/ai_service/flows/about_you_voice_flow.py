# ai_service/about_you_voice_flow.py
import os, uuid, json, random, logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from transformers import pipeline
from elevenlabs import ElevenLabs
import google.generativeai as genai
from ai_service.memory_manager import MemoryManager
from ai_service.agents import get_next_question

router = APIRouter(prefix="/about_you", tags=["About You Flow"])
memory = MemoryManager()

# =========================================================
# 🗂️ PATH SETUP
# =========================================================
BASE_DIR = os.path.join(os.path.dirname(__file__), "storage", "about_you")
INPUT_DIR = os.path.join(BASE_DIR, "input")
TTS_DIR = os.path.join(BASE_DIR, "tts")
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(TTS_DIR, exist_ok=True)

ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")
client = ElevenLabs(api_key=ELEVEN_API_KEY)
genai.configure(api_key=GEMINI_KEY)

emotion_model = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    device=-1
)
asr_model = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-tiny",
    device=-1
)

QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), "knowledge", "about_you_questions.json")

# =========================================================
# 🔊 START ROUTE
# =========================================================
@router.post("/start")
async def start_about_you():
    """Starts About You section with the first question."""
    try:
        with open(QUESTIONS_PATH, "r") as f:
            questions = json.load(f)
        first = sorted(questions, key=lambda q: q["priority"])[0]
        q_text = random.choice(first["prompt_variants"])

        stream = client.text_to_speech.convert(
            voice_id="EXAVITQu4vr4xnSDxMaL",
            model_id="eleven_multilingual_v2",
            text=q_text
        )
        filename = f"q_{uuid.uuid4().hex}.mp3"
        output_path = os.path.join(TTS_DIR, filename)
        with open(output_path, "wb") as f:
            for chunk in stream:
                if isinstance(chunk, bytes):
                    f.write(chunk)

        return {
            "question_id": first["id"],
            "question_text": q_text,
            "audio_url": f"http://127.0.0.1:8000/storage/about_you/tts/{filename}"
        }
    except Exception as e:
        logging.error(f"Error in start_about_you: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =========================================================
# 🔁 REPLY ROUTE
# =========================================================
@router.post("/reply")
async def about_you_reply(
    question_id: str = Form(...),
    audio: UploadFile = File(...),
    user_id: str = Form("anonymous")
):
    """Handles user reply → emotion → reflection → adaptive next question."""
    try:
        # 1️⃣ Save uploaded audio
        audio_path = os.path.join(INPUT_DIR, f"user_{uuid.uuid4().hex}.wav")
        with open(audio_path, "wb") as f:
            f.write(await audio.read())

        # 2️⃣ Transcribe and detect emotion
        text = asr_model(audio_path)["text"].strip()
        emotion = emotion_model(text)[0]["label"].lower()

        # 3️⃣ Generate empathetic AI reply
        model = genai.GenerativeModel("models/gemini-2.0-pro")
        prompt = f"The person said '{text}' and feels {emotion}. Respond compassionately and ask one gentle follow-up."
        response = model.generate_content(prompt)
        ai_reply = response.text.strip()

        # 4️⃣ Convert AI reply to speech
        stream = client.text_to_speech.convert(
            voice_id="EXAVITQu4vr4xnSDxMaL",
            model_id="eleven_multilingual_v2",
            text=ai_reply
        )
        reply_audio_file = os.path.join(TTS_DIR, f"reply_{uuid.uuid4().hex}.mp3")
        with open(reply_audio_file, "wb") as f:
            for chunk in stream:
                if isinstance(chunk, bytes):
                    f.write(chunk)

        # 5️⃣ Save turn to memory
        memory.add_turn(user_id, text, ai_reply, emotion)

        # 6️⃣ Generate next adaptive question via CrewAI
        crew_result = get_next_question(
            user_id=user_id,
            last_response=text,
            detected_emotion=emotion
        )
        next_question = crew_result["next_question"]

        # 7️⃣ Convert next question to speech
        next_audio_stream = client.text_to_speech.convert(
            voice_id="EXAVITQu4vr4xnSDxMaL",
            model_id="eleven_multilingual_v2",
            text=next_question
        )
        next_audio_file = os.path.join(TTS_DIR, f"next_{uuid.uuid4().hex}.mp3")
        with open(next_audio_file, "wb") as f:
            for chunk in next_audio_stream:
                if isinstance(chunk, bytes):
                    f.write(chunk)

        # 8️⃣ Return all outputs
        return {
            "user_text": text,
            "emotion": emotion,
            "ai_reply": ai_reply,
            "ai_audio_url": f"http://127.0.0.1:8000/storage/about_you/tts/{os.path.basename(reply_audio_file)}",
            "next_question": next_question,
            "next_audio_url": f"http://127.0.0.1:8000/storage/about_you/tts/{os.path.basename(next_audio_file)}"
        }

    except Exception as e:
        logging.error(f"Error in About You flow: {e}")
        raise HTTPException(status_code=500, detail=str(e))
