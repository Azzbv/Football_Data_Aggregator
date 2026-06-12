import asyncio
import logging
from ingestion.pipelines.ingest_understat import ingest_understat
from app.core.database import connect_to_mongo, close_mongo_connection
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """Test script to ingest a small subset of Understat data."""
    await connect_to_mongo()
    try:
        target_leagues = ['EPL']
        target_years = [2023]
        logger.info('Starting test ingestion for Understat (Mock Mode)...')
        result = await ingest_understat(leagues=target_leagues, years=target_years, limit_matches=3, use_mock=True)
        logger.info(f'Final Ingestion Results: {result}')
    except Exception as e:
        logger.error(f'Ingestion failed: {e}')
    finally:
        await close_mongo_connection()
if __name__ == '__main__':
    asyncio.run(main())