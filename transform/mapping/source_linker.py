from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase

class SourceLinker:
    """Handles the creation and management of source_links for provenance."""

    def __init__(self, unified_db: AsyncIOMotorDatabase):
        self.db = unified_db

    async def link(self, unified_id: str, entity_type: str, source_name: str, source_id: str, source_db: str, source_collection: str):
        """Create a link between a unified entity and its raw source counterpart."""
        link_doc = {'unified_id': unified_id, 'entity_type': entity_type, 'source_name': source_name, 'source_id': str(source_id), 'source_db': source_db, 'source_collection': source_collection, 'linked_at': datetime.now(timezone.utc)}
        await self.db['source_links'].update_one({'unified_id': unified_id, 'source_name': source_name, 'source_id': str(source_id)}, {'$set': link_doc}, upsert=True)