from fastapi import APIRouter, UploadFile, File, Query
import tempfile
from pathlib import Path
from fastapi.responses import FileResponse

from ai_service.test_flow.interactive_flow import run_conversation
from ai_service.db.patient_session_repository import save_patient_response
from ai_service.db.conversation_store import save_conversation_entry


router = APIRouter()

@router.get("/test/start")
async def start_interactive():
    """Start the interactive Q&A voice session."""
    return start_conversation()

@router.post("/test/voice")
async def respond_to_voice(
    audio: UploadFile = File(...),
    patient_id: str = Query("P001"),
    category: str = Query("Introduction")
):
    """Process user's voice answer and return next question (text + audio)."""
    try:
        # Save temp audio file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await audio.read())
            tmp_path = tmp.name

        # Run AI conversation flow
        result = run_conversation(tmp_path)

        # Store each exchange in MongoDB
        await save_conversation_entry(
            patient_id=patient_id,
            category=category,
            ai_question=result.get("ai_reply", "N/A"),
            user_text=result.get("transcript", "N/A"),
            ai_reply=result.get("next_question_text", "N/A")
        )

        return result

    except Exception as e:
        return {"error": str(e)}


@router.get("/test/play/{filename}")
async def play_audio(filename: str):
    """Serve generated audio files directly."""
    file_path = Path("ai_service/static/audio") / filename
    if file_path.exists():
        return FileResponse(file_path, media_type="audio/mpeg")
    return {"error": "Audio file not found."}

@router.get("/conversation/categories")
async def get_categories():
    """Return the list of available conversation categories."""
    categories = [
        {"name": "Introduction"},
        {"name": "Wisdom (About You)"},
        {"name": "Places"},
        {"name": "Life Events - Early Childhood"},
        {"name": "Life Events - Teen"},
        {"name": "Life Events - Post Secondary"},
        {"name": "Life Events - Adulthood"},
        {"name": "Life Events - Present"},
        {"name": "Family - Partner"},
        {"name": "Family - Past Partners"},
        {"name": "Family - Children"},
        {"name": "Family - Parenting"},
        {"name": "Family - Family General"},
        {"name": "Family - Mother"},
        {"name": "Family - Father / Parents"},
        {"name": "Family - Siblings"},
        {"name": "Family - Grandparents"},
        {"name": "Family - Pets"},
    ]
    return {"categories": categories}
