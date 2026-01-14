import tempfile
from fastapi import APIRouter, File, UploadFile
from ai_service.conversation.interactive_flow import run_conversation

router = APIRouter()

@router.post("/test/voice")
async def respond_to_voice(audio: UploadFile = File(...)):
    """Processes user's recorded voice and returns next question."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await audio.read())
            tmp_path = tmp.name

        # Run synchronously (old stable version)
        result = run_conversation(tmp_path)
        return result

    except Exception as e:
        print(f"❌ Voice processing failed: {e}")
        return {"error": str(e)}
