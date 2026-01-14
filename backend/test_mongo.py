import asyncio
from ai_service.db.mongo_client import test_connection

asyncio.run(test_connection())
