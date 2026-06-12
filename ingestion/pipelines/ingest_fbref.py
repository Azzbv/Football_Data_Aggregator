import logging
import uuid
from typing import List, Optional, Dict, Any
from app.core.database import get_db_fbref
from app.services.raw_browser import RawRepository
from ingestion.sources.fbref_adapter import FBrefAdapter
from ingestion.base.source_adapter import LoaderResult
logger = logging.getLogger(__name__)

async def ingest_fbref(league_id: str, season: str, use_mock: bool=False):
    """
    Pipeline to ingest FBref data.
    Processes seasons -> matches -> player_stats/team_stats.
    """
    run_id = str(uuid.uuid4())
    db = get_db_fbref()
    adapter = FBrefAdapter(use_mock=use_mock)
    result = LoaderResult('FBref')
    try:
        logger.info(f'Starting FBref ingestion run: {run_id}')
        match_repo = RawRepository(db['matches'], 'fbref', 'match')
        player_stats_repo = RawRepository(db['player_stats'], 'fbref', 'player_stat')
        team_stats_repo = RawRepository(db['team_stats'], 'fbref', 'team_stat')
        logger.info(f'Ingesting FBref matches for league {league_id} season {season}')
        matches = await adapter.get_season_results(league_id, season)
        if matches:
            await match_repo.bulk_upsert(matches, 'id', run_id)
            result.add_count('matches', len(matches))
            for match in matches:
                m_id = match['id']
                p_stats = await adapter.get_player_stats(m_id)
                if p_stats:
                    await player_stats_repo.upsert(str(m_id), {'match_id': m_id, 'stats': p_stats}, run_id)
                    result.add_count('player_stat_sets', 1)
                t_stats = await adapter.get_team_stats(m_id)
                if t_stats:
                    await team_stats_repo.upsert(str(m_id), {'match_id': m_id, 'stats': t_stats}, run_id)
                    result.add_count('team_stat_sets', 1)
        logger.info(f'FBref ingestion complete. {result}')
        return result
    finally:
        await adapter.close()