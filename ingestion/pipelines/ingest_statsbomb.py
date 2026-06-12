import logging
import uuid
from datetime import datetime
from typing import List, Optional
from app.core.database import get_db_statsbomb
from app.services.raw_browser import RawRepository
from ingestion.sources.statsbomb_adapter import StatsBombAdapter
from ingestion.base.source_adapter import LoaderResult
logger = logging.getLogger(__name__)

async def ingest_statsbomb(competition_ids: Optional[List[int]]=None):
    """
    Pipeline to ingest StatsBomb Open Data.
    Processes competitions -> matches -> lineups -> events.
    """
    run_id = str(uuid.uuid4())
    db = get_db_statsbomb()
    adapter = StatsBombAdapter()
    result = LoaderResult('StatsBomb')
    try:
        logger.info(f'Starting StatsBomb ingestion run: {run_id}')
        competitions = await adapter.get_competitions()
        if not competitions:
            logger.warning('No competitions found.')
            return result
        if competition_ids:
            competitions = [c for c in competitions if c['competition_id'] in competition_ids]
        comp_repo = RawRepository(db['competitions'], 'statsbomb', 'competition')
        for comp in competitions:
            comp_source_id = f"{comp['competition_id']}_{comp['season_id']}"
            await comp_repo.upsert(comp_source_id, comp, run_id)
        result.add_count('competitions_seasons', len(competitions))
        logger.info(f'Ingested {len(competitions)} competition-season pairs')
        match_repo = RawRepository(db['matches'], 'statsbomb', 'match')
        lineup_repo = RawRepository(db['lineups'], 'statsbomb', 'lineup')
        event_repo = RawRepository(db['events'], 'statsbomb', 'event')
        for comp in competitions:
            c_id = comp['competition_id']
            s_id = comp['season_id']
            matches = await adapter.get_matches(c_id, s_id)
            if not matches:
                continue
            await match_repo.bulk_upsert(matches, 'match_id', run_id)
            result.add_count('matches', len(matches))
            for match in matches:
                m_id = match['match_id']
                lineups = await adapter.get_lineups(m_id)
                if lineups:
                    await lineup_repo.upsert(str(m_id), {'match_id': m_id, 'lineups': lineups}, run_id)
                    result.add_count('lineups', 1)
                events = await adapter.get_events(m_id)
                if events:
                    for event in events:
                        event['match_id'] = m_id
                    await event_repo.bulk_upsert(events, 'id', run_id)
                    result.add_count('events', len(events))
            logger.info(f'Finished processing competition {c_id} season {s_id}')
        logger.info(f'StatsBomb ingestion complete. {result}')
        return result
    finally:
        await adapter.close()