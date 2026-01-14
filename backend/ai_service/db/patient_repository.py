from ai_service.db.mongo_client import db, serialize_doc
from ai_service.models.patient_session import PatientSession

async def save_patient_response(session: PatientSession):
    result = await db.patient_sessions.insert_one(session.model_dump())
    return str(result.inserted_id)

async def get_patient_sessions(patient_id: str):
    cursor = db.patient_sessions.find({"patient_id": patient_id})
    sessions = [serialize_doc(s) async for s in cursor]
    return sessions
async def get_latest_patient_response(patient_id: str, category: str):
    """Fetch the most recent saved answer for this category/patient."""
    doc = await db.patient_sessions.find_one(
        {"patient_id": patient_id, "category": category},
        sort=[("timestamp", -1)]
    )
    if doc:
        return serialize_doc(doc)
    return None
 