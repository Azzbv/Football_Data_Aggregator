from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    statsbomb_raw = None
    understat_raw = None
    fbref_raw = None
    unified = None
db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.statsbomb_raw = db.client[settings.MONGODB_DB_STATSBOMB_RAW]
    db.understat_raw = db.client[settings.MONGODB_DB_UNDERSTAT_RAW]
    db.fbref_raw = db.client[settings.MONGODB_DB_FBREF_RAW]
    db.unified = db.client[settings.MONGODB_DB_UNIFIED]

async def close_mongo_connection():
    if db.client:
        db.client.close()

def get_db_statsbomb():
    return db.statsbomb_raw

def get_db_understat():
    return db.understat_raw

def get_db_fbref():
    return db.fbref_raw

def get_db_unified():
    return db.unified

async def ping_databases():
    """Simple health check to ping all configured databases."""
    if not db.client:
        return False
    try:
        await db.client.admin.command('ping')
        return True
    except Exception:
        return False