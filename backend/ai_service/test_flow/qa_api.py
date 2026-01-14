from fastapi import APIRouter, UploadFile, File
import tempfile, os
from ai_service.test_flow.qa_two_agent_flow import run_two_agent_test

router = APIRouter(prefix="/test", tags=["QA Test Flow"])

@router.post("/voice")
async def test_voice(audio: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await audio.read())
            tmp_path = tmp.name

        result = run_two_agent_test(tmp_path)
        os.remove(tmp_path)
        return result

    except Exception as e:
        return {"error": str(e)}
