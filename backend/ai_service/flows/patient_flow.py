# ai_service/flows/patient_flow.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/profile", tags=["Patient Session"])

class PatientMessage(BaseModel):
    user_id: str
    message: str

memory_store = {}

@router.post("/{patient_id}")
async def handle_patient_message(patient_id: str, payload: PatientMessage):
    """Store a message for a patient (in memory for now)."""
    try:
        if patient_id not in memory_store:
            memory_store[patient_id] = []
        memory_store[patient_id].append(payload.message)
        return {
            "patient_id": patient_id,
            "stored_messages": memory_store[patient_id],
            "message": "Message stored successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
