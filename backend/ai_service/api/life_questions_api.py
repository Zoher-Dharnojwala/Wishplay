from fastapi import APIRouter, Query
from ai_service.db import get_history  # <-- IMPORT THE CORRECT FUNCTION

router = APIRouter(prefix="/conversation/history")


@router.get("/list")
async def history_list(user_id: str = Query(...)):
    rows = get_history(user_id)

    return {
        "status": "success",
        "history": rows
    }
