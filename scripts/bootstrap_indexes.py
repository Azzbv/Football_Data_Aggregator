import asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import connect_to_mongo, close_mongo_connection, db
from app.core.config import settings
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def bootstrap_indexes():
    """Create indexes for all raw and unified collections with proper constraints."""
    await connect_to_mongo()
    index_configs = {settings.MONGODB_DB_STATSBOMB_RAW: {'competitions': [('metadata.source_id', True)], 'matches': [('metadata.source_id', True), 'season_id', 'competition_id'], 'events': [('metadata.source_id', True), 'match_id', 'player_id'], 'lineups': [('metadata.source_id', True), 'match_id']}, settings.MONGODB_DB_UNDERSTAT_RAW: {'matches': [('metadata.source_id', True), 'season'], 'shots': [('metadata.source_id', True), 'match_id']}, settings.MONGODB_DB_FBREF_RAW: {'matches': [('metadata.source_id', True), 'season']}, settings.MONGODB_DB_UNIFIED: {'competitions': [('unified_id', True)], 'seasons': [('unified_id', True), 'competition_id'], 'teams': [('unified_id', True), ('normalized_name', True)], 'players': [('unified_id', True), ('normalized_name', True)], 'matches': [('unified_id', True), 'competition_id', 'season_id', 'match_date'], 'source_links': [([('source_name', 1), ('source_id', 1), ('entity_type', 1)], True), 'unified_id'], 'identity_mappings': [([('type', 1), ('alias', 1)], True), 'canonical_id'], 'transformation_runs': [('run_id', True), 'entity_type', 'status']}}
    for db_name, collections in index_configs.items():
        if db_name not in db.client.list_database_names:
            pass
        database = db.client[db_name]
        logger.info(f'Bootstrapping indexes for database: {db_name}')
        for coll_name, definitions in collections.items():
            collection = database[coll_name]
            for definition in definitions:
                unique = False
                if isinstance(definition, tuple):
                    fields, unique = definition
                else:
                    fields = definition
                logger.info(f'Creating index on {coll_name}: {fields} (unique={unique})')
                try:
                    await collection.create_index(fields, unique=unique)
                except Exception as e:
                    logger.error(f'Failed to create index on {coll_name}: {e}')
    await close_mongo_connection()
    logger.info('Indexing complete.')
if __name__ == '__main__':
    asyncio.run(bootstrap_indexes())