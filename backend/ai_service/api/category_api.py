from fastapi import APIRouter
from ai_service.db.category_repository import get_all_categories

router = APIRouter()

@router.get("/categories")
async def list_categories():
    """Return all available conversation categories."""
    categories = await get_all_categories()
    return {"categories": categories}
