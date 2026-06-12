import asyncio
import logging
from ingestion.pipelines.ingest_fbref import ingest_fbref
from app.core.database import connect_to_mongo, close_mongo_connection
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """Test script to ingest FBref data (Mock Mode)."""
    await connect_to_mongo()
    try:
        logger.info('Starting test ingestion for FBref (Mock Mode)...')
        result = await ingest_fbref(league_id='9', season='2023-2024', use_mock=True)
        logger.info(f'Final Ingestion Results: {result}')
    except Exception as e:
        logger.error(f'Ingestion failed: {e}')
    finally:
        await close_mongo_connection()
if __name__ == '__main__':
    asyncio.run(main())