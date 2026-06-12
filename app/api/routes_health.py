from fastapi import APIRouter
from app.core.database import ping_databases
from app.core.config import settings
router = APIRouter()

@router.get('')
async def health_check():
    mongo_alive = await ping_databases()
    return {'status': 'ok' if mongo_alive else 'degraded', 'project': settings.PROJECT_NAME, 'database': 'connected' if mongo_alive else 'disconnected', 'version': '1.0.0'}