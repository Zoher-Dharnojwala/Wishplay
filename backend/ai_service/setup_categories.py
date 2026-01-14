import asyncio
from ai_service.db.category_repository import save_categories

categories = [
    "Introduction",
    "Wisdom (About You)",
    "Places",
    "Life Events - Early Childhood",
    "Life Events - Teen",
    "Life Events - Post Secondary",
    "Life Events - Adulthood",
    "Life Events - Present",
    "Family - Partner",
    "Family - Past Partners",
    "Family - Children",
    "Family - Parenting",
    "Family - Family General",
    "Family - Mother",
    "Family - Father / Parents",
    "Family - Siblings",
    "Family - Grandparents",
    "Family - Pets",
]

async def main():
    result = await save_categories(categories)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
