from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import tempfile, subprocess, os
import base64

from ai_service.services.text_to_speech_tool import tts_full, tts_stream
from ai_service.services.stt import transcribe_audio
from ai_service.services.brain import SessionBrain
from ai_service.db import save_history, get_history

router = APIRouter(prefix="/conversation")

# Store user sessions in memory
sessions = {}


# ---------------------------------------------------
# SSE Helper
# ---------------------------------------------------
def sse(event, data):
    return f"event: {event}\ndata: {data}\n\n"


# ---------------------------------------------------
# START CONVERSATION
# ---------------------------------------------------
@router.get("/start")
async def start_conversation(patient_id: str, category: str):

    # Create session if first time
    if patient_id not in sessions:
        sessions[patient_id] = SessionBrain()

    # First question
    text = f"Let's talk about {category.lower()}. Can you tell me a bit about yourself?"

    # Save internally as "last question"
    sessions[patient_id].last_question = text
    sessions[patient_id].last_category = category

    # TTS output
    audio_b64 = await tts_full(text)

    return {
        "question_id": "Q1",
        "first_question_text": text,
        "first_question_audio": audio_b64,
    }


# ---------------------------------------------------
# STREAMING REPLY (main conversation loop)
# ---------------------------------------------------
@router.post("/reply/stream")
async def reply_stream(
    patient_id: str = Form(...),
    question_id: str = Form(...),
    category: str = Form(...),
    audio: UploadFile = File(...)
):

    session = sessions.get(patient_id)
    if not session:
        raise RuntimeError("❌ NO SESSION — call /start first")

    async def stream_logic():

        # ---------------------------------------------------
        # SAVE AUDIO → TRANSCRIBE
        # ---------------------------------------------------
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(await audio.read())
            webm = tmp.name

        wav = webm.replace(".webm", ".wav")
        subprocess.run(
            ["ffmpeg", "-i", webm, "-ar", "16000", "-ac", "1", wav, "-y"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        transcript = await transcribe_audio(wav)
        yield sse("user_transcript", transcript)

        # ---------------------------------------------------
        # AI RESPONSE
        # ---------------------------------------------------
        next_q = await session.handle_user_message(transcript, category)
        yield sse("next_question", next_q)

        # ---------------------------------------------------
        # SAVE TO DATABASE
        # ---------------------------------------------------
        try:
            save_history(
                user_id=patient_id,
                category=category,
                question=session.last_question,
                answer_text=next_q
            )
        except Exception as e:
            print("DB SAVE ERROR:", e)

        # ---------------------------------------------------
        # STREAM TTS AUDIO
        # ---------------------------------------------------
        async for audio_bytes in tts_stream(next_q):

            # audio_bytes must be bytes → ensure it
            if isinstance(audio_bytes, str):
                try:
                    audio_bytes = base64.b64decode(audio_bytes)
                except:
                    audio_bytes = audio_bytes.encode("utf-8")

            b64 = base64.b64encode(audio_bytes).decode("utf-8")

            yield sse("audio_chunk", b64)

        yield sse("audio_complete", "done")

        os.remove(webm)
        os.remove(wav)

    return StreamingResponse(
        stream_logic(),
        media_type="text/event-stream",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )





# ---------------------------------------------------
# END CONVERSATION
# ---------------------------------------------------
@router.post("/end")
async def end_conversation(
    patient_id: str = Form(...),
    category: str = Form(...),
    transcript: str = Form(...)
):
    save_history(
        user_id=patient_id,
        category=category,
        question="Full Conversation",
        answer_text=transcript
    )
    return {"status": "success"}


# ---------------------------------------------------
# HISTORY ENDPOINT
# ---------------------------------------------------
@router.get("/history/list")
async def history_list(user_id: str):
    history = get_history(user_id)
    return {"status": "success", "history": history}
