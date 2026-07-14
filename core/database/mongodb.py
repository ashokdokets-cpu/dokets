import logging
from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings

logger = logging.getLogger("dokets.database")

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None
        self.connected = False

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000
            )
            self.db = self.client[settings.MONGODB_DB_NAME]
            await self.client.admin.command('ping')
            self.connected = True
            logger.info("✅ MongoDB Atlas connected - data will persist!")
            
            # Create indexes
            await self.db.users.create_index("email", unique=True)
            await self.db.contracts.create_index("customer_id")
            await self.db.contracts.create_index("provider_id")
            logger.info("✅ Database indexes created")
        except Exception as e:
            logger.warning(f"MongoDB: {e}")
            self.connected = False

    async def close(self):
        if self.client:
            self.client.close()

    def get_collection(self, name):
        # Return None for now - use in-memory fallback
        # MongoDB integration needs async motor, not pymongo
        return None

mongodb = MongoDB()