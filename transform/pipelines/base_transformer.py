import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
logger = logging.getLogger(__name__)

class BaseTransformer:
    """Base class for all transformation pipelines."""

    def __init__(self, source_db: AsyncIOMotorDatabase, unified_db: AsyncIOMotorDatabase, source_name: str):
        self.source_db = source_db
        self.unified_db = unified_db
        self.source_name = source_name

    async def start_run(self, entity_type: str) -> str:
        """Create a transformation run record."""
        run_id = str(uuid.uuid4())
        await self.unified_db['transformation_runs'].insert_one({'run_id': run_id, 'entity_type': entity_type, 'source_name': self.source_name, 'status': 'started', 'started_at': datetime.now(timezone.utc), 'processed_count': 0})
        return run_id

    async def finish_run(self, run_id: str, count: int, status: str='completed'):
        """Update the transformation run record with results."""
        await self.unified_db['transformation_runs'].update_one({'run_id': run_id}, {'$set': {'status': status, 'finished_at': datetime.now(timezone.utc), 'processed_count': count}})