import os
import uuid
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from ai_service.tasks.about_you_tasks import execute_about_you_voice_task
from ai_service.memory_manager import MemoryManager

router = APIRouter(prefix="/ai/life_reflection", tags=["Life Reflection Flow"])
memory = MemoryManager()

BASE_DIR = "/home/ubuntu/Mimir/ai_service/storage/life_reflection"
INPUT_DIR = os.path.join(BASE_DIR, "input")
TTS_DIR = os.path.join(BASE_DIR, "tts")
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(TTS_DIR, exist_ok=True)

# =========================================================
# 🧩 STATE MODEL
# =========================================================
class LifeReflectionState(BaseModel):
    question_id: str
    question_text: str = ""
    last_audio_path: str = ""
    user_id: str = "anonymous"
    emotion: str = "neutral"


# =========================================================
# 🎬 START FLOW
# =========================================================
@router.post("/start")
async def start_reflection():
    """
    Start the Life Reflection flow — fetches first reflection question (from 'about_you_questions.json')
    and generates initial voice prompt.
    """
    try:
        questions_path = "/home/ubuntu/Mimir/ai_service/knowledge/about_you_questions.json"
        import json, random

        with open(questions_path, "r") as f:
            questions = json.load(f)
        first = sorted(questions, key=lambda q: q["priority"])[0]

        question_text = random.choice(first["prompt_variants"])

        # Use ElevenLabs or gTTS for first question
        from ai_service.tasks.about_you_tasks import generate_voice
        audio_path = generate_voice(question_text, emotion="neutral")

        return {
            "question_id": first["id"],
            "question_text": question_text,
            "audio_file": audio_path,
            "audio_url": f"http://98.94.107.151:8000/storage/life_reflection/tts/{os.path.basename(audio_path)}"
        }
    except Exception as e:
        logging.error(f"❌ Error starting Life Reflection flow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start flow: {e}")


# =========================================================
# 🎧 REPLY HANDLER
# =========================================================
@router.post("/reply")
async def reflection_reply(
    question_id: str = Form(...),
    audio: UploadFile = File(...),
    user_id: str = Form("anonymous")
):
    """
    Handles one reflection step: audio → text → emotion → reflection → voice → next question.
    """
    try:
        input_path = os.path.join(INPUT_DIR, f"reflection_{uuid.uuid4().hex}.wav")
        with open(input_path, "wb") as f:
            f.write(await audio.read())

        result = execute_about_you_voice_task(question_id, input_path)

        # Add to memory
        memory.add_turn(
            user_id,
            result.get("ai_reply", ""),
            result.get("next_question_text", ""),
            result.get("emotion", "neutral")
        )

        return result

    except Exception as e:
        logging.error(f"❌ Error in Life Reflection flow: {e}")
        raise HTTPException(status_code=500, detail=str(e))
