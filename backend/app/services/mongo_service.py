from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from typing import Optional


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None

    @classmethod
    async def connect(cls):
        """Connect to MongoDB"""
        cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
        cls.database = cls.client[settings.MONGODB_DB]
        print(f"Connected to MongoDB: {settings.MONGODB_DB}")

    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB"""
        if cls.client:
            cls.client.close()
            print("Disconnected from MongoDB")

    @classmethod
    async def get_database(cls):
        """Get database instance"""
        if not cls.database:
            await cls.connect()
        return cls.database

    @classmethod
    def get_collection(cls, name: str):
        """Get a specific collection"""
        if not cls.database:
            raise RuntimeError("Database not connected. Call connect() first.")
        return cls.database[name]


# Collection names
COLLECTION_SESSIONS = "sessions"
COLLECTION_ASSETS = "assets"
COLLECTION_OUTPUTS = "outputs"
COLLECTION_LOGS = "processing_logs"


async def create_indexes():
    """Create database indexes for performance"""
    db = await MongoDB.get_database()
    
    # Sessions indexes
    await db[COLLECTION_SESSIONS].create_index("user_id")
    await db[COLLECTION_SESSIONS].create_index("created_at")
    await db[COLLECTION_SESSIONS].create_index("status")
    
    # Assets indexes
    await db[COLLECTION_ASSETS].create_index("session_id")
    await db[COLLECTION_ASSETS].create_index("file_type")
    await db[COLLECTION_ASSETS].create_index("analysis.category")
    await db[COLLECTION_ASSETS].create_index("analysis.composite_score")
    await db[COLLECTION_ASSETS].create_index([("session_id", 1), ("analysis.composite_score", -1)])
    
    # Outputs indexes
    await db[COLLECTION_OUTPUTS].create_index("session_id")
    await db[COLLECTION_OUTPUTS].create_index("output_type")
    await db[COLLECTION_OUTPUTS].create_index("status")
    await db[COLLECTION_OUTPUTS].create_index("flagged")
    
    # Logs indexes
    await db[COLLECTION_LOGS].create_index("session_id")
    await db[COLLECTION_LOGS].create_index("asset_id")
    await db[COLLECTION_LOGS].create_index("stage")
    await db[COLLECTION_LOGS].create_index("timestamp")
    
    print("Database indexes created successfully")
