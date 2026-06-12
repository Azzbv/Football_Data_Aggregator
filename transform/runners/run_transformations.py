import asyncio
import logging
from app.core.database import connect_to_mongo, close_mongo_connection, db
from app.core.config import settings
from transform.pipelines.transform_competitions import CompetitionTransformer
from transform.pipelines.transform_teams import TeamTransformer
from transform.pipelines.transform_players import PlayerTransformer
from transform.pipelines.transform_matches import MatchTransformer
from transform.pipelines.build_stats_views import StatsTransformer
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_all_transformations():
    """Run all transformation pipelines for all sources."""
    await connect_to_mongo()
    unified_db = db.client[settings.MONGODB_DB_UNIFIED]
    sources = [{'name': 'statsbomb', 'db': db.client[settings.MONGODB_DB_STATSBOMB_RAW]}, {'name': 'understat', 'db': db.client[settings.MONGODB_DB_UNDERSTAT_RAW]}, {'name': 'fbref', 'db': db.client[settings.MONGODB_DB_FBREF_RAW]}]
    try:
        for source in sources:
            logger.info(f"--- Starting transformations for source: {source['name']} ---")
            comp_transformer = CompetitionTransformer(source['db'], unified_db, source['name'])
            await comp_transformer.transform()
            team_transformer = TeamTransformer(source['db'], unified_db, source['name'])
            await team_transformer.transform()
            player_transformer = PlayerTransformer(source['db'], unified_db, source['name'])
            await player_transformer.transform()
            match_transformer = MatchTransformer(source['db'], unified_db, source['name'])
            await match_transformer.transform()
            stats_transformer = StatsTransformer(source['db'], unified_db, source['name'])
            await stats_transformer.transform()
            logger.info(f"--- Finished transformations for source: {source['name']} ---")
    except Exception as e:
        logger.error(f'Transformation run failed: {e}')
    finally:
        await close_mongo_connection()
if __name__ == '__main__':
    asyncio.run(run_all_transformations())