import asyncio
import logging
from ingestion.pipelines.ingest_statsbomb import ingest_statsbomb
from app.core.database import connect_to_mongo, close_mongo_connection
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """Test script to ingest a small subset of StatsBomb data."""
    await connect_to_mongo()
    try:
        target_competitions = [43]
        logger.info('Starting test ingestion for StatsBomb...')
        result = await ingest_statsbomb(competition_ids=target_competitions)
        logger.info(f'Final Ingestion Results: {result}')
    except Exception as e:
        logger.error(f'Ingestion failed: {e}')
    finally:
        await close_mongo_connection()
if __name__ == '__main__':
    asyncio.run(main())