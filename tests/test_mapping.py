import asyncio
import logging
from app.core.database import connect_to_mongo, close_mongo_connection, get_db_unified
from transform.mapping.entity_resolver import EntityResolver
from transform.mapping.source_linker import SourceLinker
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Test entity resolution and source linking."""
    await connect_to_mongo()
    db = get_db_unified()
    resolver = EntityResolver(db)
    linker = SourceLinker(db)
    try:
        logger.info('Testing Team Resolution...')
        team_id = await resolver.resolve_team('Manchester United', 'England')
        logger.info(f"Resolved 'Manchester United' to: {team_id}")
        team_id_2 = await resolver.resolve_team('Man Utd')
        team_id_match = await resolver.resolve_team('manchester united')
        logger.info(f"Resolved 'manchester united' to: {team_id_match} (Match: {team_id == team_id_match})")
        logger.info('Testing Source Linking...')
        await linker.link(unified_id=team_id, entity_type='team', source_name='statsbomb', source_id='39', source_db='statsbomb_raw', source_collection='teams')
        logger.info(f'Linked {team_id} to StatsBomb team 39')
        mapping = await db['identity_mappings'].find_one({'canonical_id': team_id})
        logger.info(f"Identity mapping found: {mapping['alias']} -> {mapping['canonical_id']}")
    except Exception as e:
        logger.error(f'Test failed: {e}')
    finally:
        await close_mongo_connection()
if __name__ == '__main__':
    asyncio.run(main())