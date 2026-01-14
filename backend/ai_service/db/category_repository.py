from ai_service.db.mongo_client import db, serialize_doc

async def get_all_categories():
    """Fetch all categories."""
    cursor = db.categories.find({})
    return [serialize_doc(c) async for c in cursor]

async def save_categories(categories: list):
    """Initialize categories in the DB (run once)."""
    existing = await db.categories.count_documents({})
    if existing == 0:
        await db.categories.insert_many([{"name": c} for c in categories])
        return {"message": "✅ Categories initialized."}
    return {"message": "Categories already exist."}
