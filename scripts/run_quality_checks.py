import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.core.database import connect_to_mongo, close_mongo_connection, db
from app.core.config import settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QualityChecker:
    """Automated data quality auditor for the unified football platform."""

    def __init__(self, unified_db):
        self.db = unified_db
        self.report_id = str(uuid.uuid4())
        self.issues: List[Dict[str, Any]] = []

    def add_issue(self, entity_type: str, severity: str, message: str, details: Any=None):
        self.issues.append({'entity_type': entity_type, 'severity': severity, 'message': message, 'details': details})

    async def check_provenance(self):
        """Verify that every core unified entity has at least one source link."""
        entities = ['competitions', 'teams', 'players', 'matches']
        for entity in entities:
            logger.info(f'Checking provenance for {entity}...')
            async for item in self.db[entity].find({}):
                u_id = item['unified_id']
                link_exists = await self.db['source_links'].find_one({'unified_id': u_id})
                if not link_exists:
                    self.add_issue(entity_type=entity, severity='warning', message=f'Missing provenance for {u_id}', details={'unified_id': u_id, 'name': item.get('name') or item.get('unified_id')})

    async def check_duplicate_source_links(self):
        """Check if multiple unified entities point to the same source record."""
        pipeline = [{'$group': {'_id': {'source_name': '$source_name', 'source_id': '$source_id', 'entity_type': '$entity_type'}, 'count': {'$sum': 1}, 'unified_ids': {'$push': '$unified_id'}}}, {'$match': {'count': {'$gt': 1}}}]
        async for result in self.db['source_links'].aggregate(pipeline):
            self.add_issue(entity_type='source_link', severity='critical', message='Duplicate source mapping detected', details=result)

    async def check_orphaned_mappings(self):
        """Check for identity mappings that don't point to an existing unified entity."""
        async for mapping in self.db['identity_mappings'].find({}):
            canon_id = mapping['canonical_id']
            type_map = mapping['type']
            coll_name = f'{type_map}s'
            exists = await self.db[coll_name].find_one({'unified_id': canon_id})
            if not exists:
                self.add_issue(entity_type='identity_mapping', severity='error', message=f'Orphaned mapping: {canon_id} not found in {coll_name}', details=mapping)

    async def run_all(self):
        logger.info(f'Starting Quality Check Report: {self.report_id}')
        await self.check_provenance()
        await self.check_duplicate_source_links()
        await self.check_orphaned_mappings()
        summary = {'report_id': self.report_id, 'created_at': datetime.now(timezone.utc), 'total_issues': len(self.issues), 'critical_count': len([i for i in self.issues if i['severity'] == 'critical']), 'error_count': len([i for i in self.issues if i['severity'] == 'error']), 'warning_count': len([i for i in self.issues if i['severity'] == 'warning']), 'issues': self.issues}
        await self.db['quality_reports'].insert_one(summary)
        logger.info(f'Quality check complete. Found {len(self.issues)} issues.')
        return summary

async def main():
    await connect_to_mongo()
    checker = QualityChecker(db.client[settings.MONGODB_DB_UNIFIED])
    report = await checker.run_all()
    print(f'\n--- Quality Report Summary ---')
    print(f"ID: {report['report_id']}")
    print(f"Total Issues: {report['total_issues']}")
    print(f"Critical: {report['critical_count']}")
    print(f"Errors: {report['error_count']}")
    print(f"Warnings: {report['warning_count']}")
    await close_mongo_connection()
if __name__ == '__main__':
    asyncio.run(main())