from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import UpdateOne

class RawRepository:
    """Generic repository for raw data operations with metadata enrichment."""

    def __init__(self, collection: AsyncIOMotorCollection, source_name: str, entity_type: str):
        self.collection = collection
        self.source_name = source_name
        self.entity_type = entity_type

    def _enrich_metadata(self, data: Dict[str, Any], source_id: str, run_id: str) -> Dict[str, Any]:
        """Add source metadata to the raw payload."""
        enriched = data.copy()
        enriched['metadata'] = {'source_name': self.source_name, 'source_entity_type': self.entity_type, 'source_id': source_id, 'ingested_at': datetime.now(timezone.utc), 'ingestion_run_id': run_id}
        return enriched

    async def upsert(self, source_id: str, data: Dict[str, Any], run_id: str) -> bool:
        """Upsert a single document based on source_id."""
        enriched_data = self._enrich_metadata(data, source_id, run_id)
        result = await self.collection.update_one({'metadata.source_id': source_id}, {'$set': enriched_data}, upsert=True)
        return result.modified_count > 0 or result.upserted_id is not None

    async def bulk_upsert(self, items: List[Dict[str, Any]], id_field: str, run_id: str) -> int:
        """Perform bulk upsert of multiple documents."""
        if not items:
            return 0
        operations = []
        for item in items:
            source_id = str(item.get(id_field))
            enriched_data = self._enrich_metadata(item, source_id, run_id)
            operations.append(UpdateOne({'metadata.source_id': source_id}, {'$set': enriched_data}, upsert=True))
        result = await self.collection.bulk_write(operations)
        return result.upserted_count + result.modified_count