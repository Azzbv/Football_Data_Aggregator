import asyncio
import logging
from transform.runners.run_transformations import run_all_transformations
from scripts.run_quality_checks import main as run_quality_checks
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_pipeline():
    """Run the full transformation and quality audit pipeline."""
    logger.info('=== PHASE 1: Data Transformation ===')
    try:
        await run_all_transformations()
    except Exception as e:
        logger.error(f'Transformation phase failed: {e}')
        return
    logger.info('=== PHASE 2: Quality Audit ===')
    try:
        await run_quality_checks()
    except Exception as e:
        logger.error(f'Quality audit phase failed: {e}')
    logger.info('=== Full Pipeline Run Complete ===')
if __name__ == '__main__':
    asyncio.run(run_pipeline())