from datetime import datetime
from ai_service.db.mongo_client import db, serialize_doc

async def save_patient_response(patient_id: str, category: str, question: str, answer: str):
    """Store a patient’s response in MongoDB."""
    record = {
        "patient_id": patient_id,
        "category": category,
        "question": question,
        "answer": answer,
        "timestamp": datetime.utcnow()
    }
    result = await db.patient_sessions.insert_one(record)
    return str(result.inserted_id)

async def get_latest_response(patient_id: str, category: str):
    """Fetch the last response for this patient and category."""
    doc = await db.patient_sessions.find_one(
        {"patient_id": patient_id, "category": category},
        sort=[("timestamp", -1)]
    )
    return serialize_doc(doc) if doc else None

async def get_all_responses(patient_id: str, category: str):
    """Fetch all previous responses for review."""
    cursor = db.patient_sessions.find(
        {"patient_id": patient_id, "category": category}
    ).sort("timestamp", 1)
    return [serialize_doc(c) async for c in cursor]
