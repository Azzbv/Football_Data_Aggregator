import asyncio
import logging
from ingestion.pipelines.ingest_statsbomb import ingest_statsbomb
from ingestion.pipelines.ingest_understat import ingest_understat
from ingestion.pipelines.ingest_fbref import ingest_fbref
from app.core.database import connect_to_mongo, close_mongo_connection
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_all_ingestions():
    """Consolidated runner to ingest all top European leagues and major competitions."""
    await connect_to_mongo()
    try:
        european_leagues = [2, 11, 7, 12, 9, 16]
        logger.info(f'--- Starting Ingestion: StatsBomb (Leagues: {european_leagues}) ---')
        sb_result = await ingest_statsbomb(competition_ids=european_leagues)
        logger.info(f'StatsBomb Result: {sb_result}')
        understat_leagues = ['EPL', 'La_liga', 'Bundesliga', 'Serie_A', 'Ligue_1']
        logger.info(f'--- Starting Ingestion: Understat (Leagues: {understat_leagues}) ---')
        us_result = await ingest_understat(leagues=understat_leagues, years=[2023], limit_matches=5, use_mock=True)
        logger.info(f'Understat Result: {us_result}')
        fbref_leagues = ['9', '12', '20', '11', '13']
        logger.info(f'--- Starting Ingestion: FBref (Leagues: {fbref_leagues}) ---')
        for l_id in fbref_leagues:
            fb_result = await ingest_fbref(league_id=l_id, season='2023-2024', use_mock=True)
            logger.info(f'FBref {l_id} Result: {fb_result}')
        logger.info('--- All European Top League Ingestions Complete ---')
    except Exception as e:
        logger.error(f'Ingestion process failed: {e}')
    finally:
        await close_mongo_connection()
if __name__ == '__main__':
    asyncio.run(run_all_ingestions())