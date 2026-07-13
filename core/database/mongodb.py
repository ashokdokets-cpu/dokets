import logging
from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings

logger = logging.getLogger("dokets.database")

class InMemoryDB:
    """Simple storage for development"""
    users = []
    contracts = []

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None
        self.connected = False

    async def connect(self):
        # Use in-memory for instant startup
        self.db = InMemoryDB()
        self.connected = True
        logger.info("In-memory database ready (instant)")
        
        # Try MongoDB in background (optional)
        try:
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=2000  # Only wait 2 seconds
            )
            real_db = self.client[settings.MONGODB_DB_NAME]
            await self.client.admin.command('ping')
            self.db = real_db
            logger.info("MongoDB connected!")
        except:
            logger.info("Using in-memory storage (MongoDB not available)")

    async def close(self):
        if self.client:
            self.client.close()

mongodb = MongoDB()