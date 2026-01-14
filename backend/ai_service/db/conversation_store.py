from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "mimir_local")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
conversations = db["conversations"]

async def save_conversation_entry(patient_id, category, ai_question, user_text, ai_reply):
    entry = {
        "patient_id": patient_id,
        "category": category,
        "ai_question": ai_question,
        "user_text": user_text,
        "ai_reply": ai_reply,
        "timestamp": datetime.utcnow()
    }
    await conversations.insert_one(entry)
